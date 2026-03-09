

from django.shortcuts import render, redirect
from django.contrib.admin.sites import site
from django.db.models import Count, Sum, Max
from django.utils import timezone
from datetime import timedelta, datetime
from .models import AttackLog, Alert, ThresholdConfig, IpBlock, InstanceMapping
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.conf import settings
import json


@login_required(login_url='/login/')
def home(request):
    # Data untuk dashboard (sama seperti sebelumnya)
    last_24h = timezone.now() - timedelta(hours=24)
    
    # Total serangan
    total_attacks = AttackLog.objects.filter(
        timestamp__gte=last_24h
    ).aggregate(total=Sum('count'))['total'] or 0
    
    # Alert hari ini
    today_alerts = Alert.objects.filter(
        timestamp__date=timezone.now().date()
    ).count()
    
    # Threshold aktif
    active_thresholds = ThresholdConfig.objects.filter(is_active=True).count()
    
    # Top 10 attackers
    top_attackers = AttackLog.objects.filter(
        timestamp__gte=last_24h
    ).values('src_ip').annotate(
        total=Sum('count')
    ).order_by('-total')[:10]
    
    # Recent attack logs
    recent_attacks = AttackLog.objects.filter(
        timestamp__gte=last_24h
    ).order_by('-timestamp')[:20]
    
    # Attack types distribution
    attack_types = AttackLog.objects.filter(
        timestamp__gte=last_24h
    ).values('attack_type').annotate(
        total=Sum('count')
    ).order_by('-total')
    
    # Threshold config
    thresholds = ThresholdConfig.objects.filter(is_active=True)
    
    # Data untuk grafik (per jam)
    hourly_data = []
    for hour in range(24):
        hour_start = timezone.now().replace(minute=0, second=0, microsecond=0) - timedelta(hours=hour)
        hour_end = hour_start + timedelta(hours=1)
        count = AttackLog.objects.filter(
            timestamp__gte=hour_start,
            timestamp__lt=hour_end
        ).aggregate(total=Sum('count'))['total'] or 0
        hourly_data.append({
            'hour': hour_start.strftime('%H:00'),
            'count': count
        })
    hourly_data.reverse()
    
    # Ambil data app_list dari admin site untuk sidebar
    app_list = site.get_app_list(request)
    
    context = {
        'total_attacks': total_attacks,
        'today_alerts': today_alerts,
        'active_thresholds': active_thresholds,
        'top_attackers': top_attackers,
        'recent_attacks': recent_attacks,
        'attack_types': attack_types,
        'thresholds': thresholds,
        'hourly_data': hourly_data,
        'app_list': app_list,  # Untuk sidebar admin
    }
    
    return render(request, 'home.html', context)


#logoout
def custom_logout(request):
    """Logout dan redirect ke halaman login"""
    logout(request)
    # Hapus semua data session
    if request.session.session_key:
        request.session.flush()
    return redirect('login')


@login_required(login_url='/login/')
def attack_analysis(request):
    """Menu untuk menganalisa pola serangan dari tabel attack_logs"""
    
    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    attack_type_filter = request.GET.get('attack_type')
    severity_filter = request.GET.get('severity')
    src_ip_filter = request.GET.get('src_ip')
    
    # Base queryset
    queryset = AttackLog.objects.all()
    
    # Apply filters
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            queryset = queryset.filter(timestamp__gte=start)
        except ValueError:
            pass
    
    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            end = end.replace(hour=23, minute=59, second=59)
            queryset = queryset.filter(timestamp__lte=end)
        except ValueError:
            pass
    
    if attack_type_filter:
        queryset = queryset.filter(attack_type=attack_type_filter)
    
    if severity_filter:
        queryset = queryset.filter(severity=severity_filter)
    
    if src_ip_filter:
        queryset = queryset.filter(src_ip__icontains=src_ip_filter)
    
    # Get unique values for filter dropdowns
    attack_types = AttackLog.objects.values_list('attack_type', flat=True).distinct()
    severities = AttackLog.objects.values_list('severity', flat=True).distinct()
    
    # Analysis data
    # Top 10 attackers - dikelompokkan berdasarkan IP dan Attack Type
    top_attackers = queryset.values('src_ip', 'attack_type').annotate(
        total=Count('id')
    ).order_by('-total')[:10]
    
    # Attack types distribution
    attack_types_dist = queryset.values('attack_type').annotate(
        total=Sum('count')
    ).order_by('-total')
    
    # Severity distribution
    severity_dist = queryset.values('severity').annotate(
        total=Sum('count')
    ).order_by('-total')
    
    # Protocol distribution
    protocol_dist = queryset.values('protocol').annotate(
        total=Sum('count')
    ).order_by('-total')
    
    # Destination ports analysis
    dst_ports = queryset.exclude(dst_port__isnull=True).exclude(dst_port=0).values('dst_port').annotate(
        total=Sum('count')
    ).order_by('-total')[:10]
    
    # Attack patterns (group by attack_type + severity)
    attack_patterns = queryset.values('attack_type', 'severity').annotate(
        total=Sum('count')
    ).order_by('-total')[:20]
    
    # Get filtered attack logs for table (paginated)
    attack_logs = queryset.order_by('-timestamp')[:100]
    
    # Total count
    total_count = queryset.aggregate(total=Sum('count'))['total'] or 0
    
    context = {
        'attack_logs': attack_logs,
        'top_attackers': top_attackers,
        'attack_types_dist': attack_types_dist,
        'severity_dist': severity_dist,
        'protocol_dist': protocol_dist,
        'dst_ports': dst_ports,
        'attack_patterns': attack_patterns,
        'total_count': total_count,
        'attack_types': attack_types,
        'severities': severities,
        # Keep filter values in context
        'start_date': start_date,
        'end_date': end_date,
        'attack_type_filter': attack_type_filter,
        'severity_filter': severity_filter,
        'src_ip_filter': src_ip_filter,
    }
    
    return render(request, 'attack_analysis.html', context)


# ============ IP BLOCKING VIEWS ============

@login_required(login_url='/login/')
def ip_block_list(request):
    """Menampilkan daftar IP yang akan di-block"""
    
    # Get all IP blocks
    ip_blocks = IpBlock.objects.all()
    
    # Get statistics
    pending_count = ip_blocks.filter(status='pending').count()
    blocked_count = ip_blocks.filter(status='blocked').count()
    
    context = {
        'ip_blocks': ip_blocks,
        'pending_count': pending_count,
        'blocked_count': blocked_count,
    }
    
    return render(request, 'ip_block_list.html', context)


def add_to_block_list(request):
    """Menambahkan IP ke daftar block (manual)"""
    
    if request.method == 'POST':
        src_ip = request.POST.get('src_ip')
        reason = request.POST.get('reason', 'Manual block')
        severity = request.POST.get('severity', 'High')
        attack_count = request.POST.get('attack_count', 1)
        
        # Check if IP already exists
        existing = IpBlock.objects.filter(src_ip=src_ip, status='pending').first()
        
        if existing:
            # Update existing record
            existing.attack_count += int(attack_count)
            existing.reason = reason
            existing.save()
            message = f'IP {src_ip} sudah ada,数据进行更新'
        else:
            # Create new record
            IpBlock.objects.create(
                src_ip=src_ip,
                reason=reason,
                attack_count=int(attack_count),
                severity=severity,
                status='pending'
            )
            message = f'IP {src_ip} berhasil ditambahkan ke daftar block'
        
        return JsonResponse({'status': 'success', 'message': message})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def auto_add_to_block_list(request):
    """Otomatis menambahkan IP ke daftar block berdasarkan threshold"""
    # Threshold: High/Critical severity ATAU attack_count > 20
    
    # Get IPs with High/Critical severity
    high_severity_ips = AttackLog.objects.filter(
        severity__in=['High', 'Critical']
    ).values('src_ip').annotate(
        total_count=Sum('count'),
        max_severity=Max('severity')
    ).filter(total_count__gte=1)
    
    # Get IPs with high attack count (>20)
    high_count_ips = AttackLog.objects.values('src_ip').annotate(
        total_count=Sum('count')
    ).filter(total_count__gt=20)
    
    added_count = 0
    
    # Process high severity IPs
    for ip_data in high_severity_ips:
        src_ip = ip_data['src_ip']
        severity = ip_data['max_severity']
        attack_count = ip_data['total_count']
        
        # Check if already exists
        existing = IpBlock.objects.filter(src_ip=src_ip, status__in=['pending', 'blocked']).first()
        
        if not existing:
            IpBlock.objects.create(
                src_ip=src_ip,
                reason=f'Auto-added: {severity} severity attack',
                attack_count=attack_count,
                severity=severity,
                status='pending'
            )
            added_count += 1
    
    # Process high count IPs
    for ip_data in high_count_ips:
        src_ip = ip_data['src_ip']
        attack_count = ip_data['total_count']
        
        # Check if already exists
        existing = IpBlock.objects.filter(src_ip=src_ip, status__in=['pending', 'blocked']).first()
        
        if not existing:
            IpBlock.objects.create(
                src_ip=src_ip,
                reason=f'Auto-added: High attack count ({attack_count} attacks)',
                attack_count=attack_count,
                severity='Critical',
                status='pending'
            )
            added_count += 1
    
    return JsonResponse({
        'status': 'success', 
        'message': f'Berhasil menambahkan {added_count} IP ke daftar block'
    })


def get_security_groups(request):
    """Mendapatkan daftar Security Groups dari Alibaba Cloud"""
    
    try:
        from aliyunsdkcore.client import AcsClient
        from aliyunsdkcore.request import CommonRequest
        
        access_key = getattr(settings, 'ALIYUN_ACCESS_KEY', '')
        access_secret = getattr(settings, 'ALIYUN_ACCESS_SECRET', '')
        region_id = getattr(settings, 'ALIYUN_REGION_ID', 'ap-southeast-3')
        
        if not access_key or not access_secret:
            return JsonResponse({
                'status': 'error', 
                'message': 'Alibaba Cloud credentials not configured'
            })
        
        client = AcsClient(access_key, access_secret, region_id)
        
        req = CommonRequest()
        req.set_accept_format('json')
        req.set_domain('ecs.aliyuncs.com')
        req.set_method('POST')
        req.set_protocol_type('https')
        req.set_version('2014-05-26')
        req.add_query_param('Action', 'DescribeSecurityGroups')
        req.add_query_param('RegionId', region_id)
        
        response = client.do_action_with_exception(req)
        result = json.loads(response.decode('utf-8'))
        
        security_groups = []
        if 'SecurityGroups' in result and 'SecurityGroup' in result['SecurityGroups']:
            for sg in result['SecurityGroups']['SecurityGroup']:
                security_groups.append({
                    'id': sg['SecurityGroupId'],
                    'name': sg['SecurityGroupName'],
                    'vpc_id': sg.get('VpcId', '')
                })
        
        return JsonResponse({
            'status': 'success',
            'security_groups': security_groups
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })


def block_ip(request, block_id):
    """Melakukan blocking IP ke Alibaba Cloud Security Group"""
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            security_group_id = data.get('security_group_id')
            
            # Get IP Block record
            ip_block = IpBlock.objects.get(id=block_id)
            
            # Check if credentials are configured
            access_key = getattr(settings, 'ALIYUN_ACCESS_KEY', '')
            access_secret = getattr(settings, 'ALIYUN_ACCESS_SECRET', '')
            region_id = getattr(settings, 'ALIYUN_REGION_ID', 'ap-southeast-3')
            
            if not access_key or not access_secret:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Alibaba Cloud credentials not configured. Please fill ALIYUN_ACCESS_KEY and ALIYUN_ACCESS_SECRET in settings.py'
                })
            
            # Block IP using Alibaba Cloud SDK
            from aliyunsdkcore.client import AcsClient
            from aliyunsdkcore.request import CommonRequest
            
            client = AcsClient(access_key, access_secret, region_id)
            
            req = CommonRequest()
            req.set_accept_format('json')
            req.set_domain('ecs.aliyuncs.com')
            req.set_method('POST')
            req.set_protocol_type('https')
            req.set_version('2014-05-26')
            req.add_query_param('Action', 'AuthorizeSecurityGroup')
            req.add_query_param('RegionId', region_id)
            req.add_query_param('SecurityGroupId', security_group_id)
            req.add_query_param('IpProtocol', 'all')
            req.add_query_param('SourceCidrIp', ip_block.src_ip + '/32')
            req.add_query_param('Policy', 'Drop')
            req.add_query_param('Description', f'Blocked by SOC - {ip_block.reason}')
            
            response = client.do_action_with_exception(req)
            
            # Update IP Block status
            ip_block.status = 'blocked'
            ip_block.security_group_id = security_group_id
            ip_block.blocked_at = timezone.now()
            ip_block.save()
            
            return JsonResponse({
                'status': 'success',
                'message': f'IP {ip_block.src_ip} berhasil di-block di Security Group {security_group_id}'
            })
            
        except IpBlock.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'IP Block record not found'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error blocking IP: {str(e)}'
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })


# ============ INSTANCE MAPPING VIEWS ============

@login_required(login_url='/login/')
def instance_mapping_list(request):
    """Menampilkan daftar instance mapping"""
    
    instances = InstanceMapping.objects.filter(is_active=True)
    
    context = {
        'instances': instances,
    }
    
    return render(request, 'instance_mapping.html', context)


def sync_instances(request):
    """Sync instances dari Alibaba Cloud ke database"""
    
    try:
        from aliyunsdkcore.client import AcsClient
        from aliyunsdkcore.request import CommonRequest
        
        access_key = getattr(settings, 'ALIYUN_ACCESS_KEY', '')
        access_secret = getattr(settings, 'ALIYUN_ACCESS_SECRET', '')
        region_id = getattr(settings, 'ALIYUN_REGION_ID', 'ap-southeast-3')
        
        if not access_key or not access_secret:
            return JsonResponse({
                'status': 'error', 
                'message': 'Alibaba Cloud credentials not configured'
            })
        
        client = AcsClient(access_key, access_secret, region_id)
        
        # Get all instances
        req = CommonRequest()
        req.set_accept_format('json')
        req.set_domain('ecs.aliyuncs.com')
        req.set_method('POST')
        req.set_protocol_type('https')
        req.set_version('2014-05-26')
        req.add_query_param('Action', 'DescribeInstances')
        req.add_query_param('RegionId', region_id)
        req.add_query_param('PageSize', '100')
        
        response = client.do_action_with_exception(req)
        result = json.loads(response.decode('utf-8'))
        
        added_count = 0
        updated_count = 0
        
        if 'Instances' in result and 'Instance' in result['Instances']:
            for instance in result['Instances']['Instance']:
                hostname = instance.get('InstanceName', '')
                instance_id = instance.get('InstanceId', '')
                public_ip = instance.get('PublicIpAddress', {}).get('IpAddress', [''])[0] if instance.get('PublicIpAddress') else None
                private_ip = instance.get('InnerIpAddress', {}).get('IpAddress', [''])[0] if instance.get('InnerIpAddress') else None
                
                # Get security groups
                security_group_ids = instance.get('SecurityGroupIds', {}).get('SecurityGroupId', [])
                if isinstance(security_group_ids, str):
                    security_group_ids = [security_group_ids]
                
                # Create or update instance mapping
                for sg_id in security_group_ids:
                    mapping, created = InstanceMapping.objects.update_or_create(
                        hostname=hostname,
                        instance_id=instance_id,
                        defaults={
                            'public_ip': public_ip,
                            'private_ip': private_ip,
                            'security_group_id': sg_id,
                            'region_id': region_id,
                            'is_active': True,
                        }
                    )
                    
                    if created:
                        added_count += 1
                    else:
                        updated_count += 1
        
        return JsonResponse({
            'status': 'success',
            'message': f'Successfully synced: {added_count} new, {updated_count} updated instances'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })


def add_instance_mapping(request):
    """Menambahkan instance mapping secara manual"""
    
    if request.method == 'POST':
        hostname = request.POST.get('hostname')
        instance_id = request.POST.get('instance_id')
        public_ip = request.POST.get('public_ip')
        private_ip = request.POST.get('private_ip')
        security_group_id = request.POST.get('security_group_id')
        security_group_name = request.POST.get('security_group_name', '')
        
        if not hostname or not security_group_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Hostname and Security Group are required'
            })
        
        # Check if exists
        existing = InstanceMapping.objects.filter(hostname=hostname).first()
        
        if existing:
            # Update
            existing.instance_id = instance_id
            existing.public_ip = public_ip
            existing.private_ip = private_ip
            existing.security_group_id = security_group_id
            existing.security_group_name = security_group_name
            existing.save()
            message = f'Instance {hostname} updated successfully'
        else:
            # Create
            InstanceMapping.objects.create(
                hostname=hostname,
                instance_id=instance_id,
                public_ip=public_ip,
                private_ip=private_ip,
                security_group_id=security_group_id,
                security_group_name=security_group_name,
            )
            message = f'Instance {hostname} added successfully'
        
        return JsonResponse({'status': 'success', 'message': message})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def delete_instance_mapping(request, mapping_id):
    """Menghapus instance mapping"""
    
    if request.method == 'POST':
        try:
            mapping = InstanceMapping.objects.get(id=mapping_id)
            mapping.is_active = False
            mapping.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Instance mapping deleted successfully'
            })
        except InstanceMapping.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Instance mapping not found'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def unblock_ip(request, block_id):
    """Melakukan unblock IP dari Alibaba Cloud Security Group"""
    
    if request.method == 'POST':
        try:
            ip_block = IpBlock.objects.get(id=block_id)
            
            if not ip_block.security_group_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No Security Group associated with this block'
                })
            
            access_key = getattr(settings, 'ALIYUN_ACCESS_KEY', '')
            access_secret = getattr(settings, 'ALIYUN_ACCESS_SECRET', '')
            region_id = getattr(settings, 'ALIYUN_REGION_ID', 'ap-southeast-3')
            
            if not access_key or not access_secret:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Alibaba Cloud credentials not configured'
                })
            
            # Unblock IP using Alibaba Cloud SDK
            from aliyunsdkcore.client import AcsClient
            from aliyunsdkcore.request import CommonRequest
            
            client = AcsClient(access_key, access_secret, region_id)
            
            req = CommonRequest()
            req.set_accept_format('json')
            req.set_domain('ecs.aliyuncs.com')
            req.set_method('POST')
            req.set_protocol_type('https')
            req.set_version('2014-05-26')
            req.add_query_param('Action', 'RevokeSecurityGroup')
            req.add_query_param('RegionId', region_id)
            req.add_query_param('SecurityGroupId', ip_block.security_group_id)
            req.add_query_param('IpProtocol', 'all')
            req.add_query_param('SourceCidrIp', ip_block.src_ip + '/32')
            req.add_query_param('Policy', 'Drop')
            
            response = client.do_action_with_exception(req)
            
            # Update IP Block status
            ip_block.status = 'unblocked'
            ip_block.save()
            
            return JsonResponse({
                'status': 'success',
                'message': f'IP {ip_block.src_ip} berhasil di-unblock'
            })
            
        except IpBlock.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'IP Block record not found'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error unblocking IP: {str(e)}'
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })


# ============ DELETE DATA VIEWS ============

@login_required(login_url='/login/')
def delete_attack_logs(request):
    """Menghapus attack logs berdasarkan filter tanggal"""
    
    if request.method == 'POST':
        try:
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            
            if not start_date or not end_date:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Start date and end date are required'
                })
            
            # Parse dates
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            end = end.replace(hour=23, minute=59, second=59)
            
            # Delete matching records
            deleted_count, _ = AttackLog.objects.filter(
                timestamp__gte=start,
                timestamp__lte=end
            ).delete()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Berhasil menghapus {deleted_count} data attack logs'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error deleting data: {str(e)}'
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })


@login_required(login_url='/login/')
def delete_alerts(request):
    """Menghapus alerts berdasarkan filter tanggal"""
    
    if request.method == 'POST':
        try:
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            
            if not start_date or not end_date:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Start date and end date are required'
                })
            
            # Parse dates
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            end = end.replace(hour=23, minute=59, second=59)
            
            # Delete matching records
            deleted_count, _ = Alert.objects.filter(
                timestamp__gte=start,
                timestamp__lte=end
            ).delete()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Berhasil menghapus {deleted_count} data alerts'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error deleting data: {str(e)}'
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })


@login_required(login_url='/login/')
def delete_threshold_config(request):
    """Menghapus threshold config berdasarkan filter"""
    
    if request.method == 'POST':
        try:
            threshold_ids = request.POST.getlist('threshold_ids')
            
            if not threshold_ids:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No thresholds selected'
                })
            
            # Delete selected thresholds
            deleted_count = ThresholdConfig.objects.filter(
                id__in=threshold_ids
            ).delete()[0]
            
            return JsonResponse({
                'status': 'success',
                'message': f'Berhasil menghapus {deleted_count} threshold config'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error deleting data: {str(e)}'
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })


@login_required(login_url='/login/')
def delete_data(request):
    """Halaman untuk menghapus data dari berbagai tabel"""
    
    # Get all thresholds for selection
    thresholds = ThresholdConfig.objects.all()
    
    context = {
        'thresholds': thresholds,
    }
    
    return render(request, 'delete_data.html', context)


@login_required(login_url='/login/')
def edit_threshold_config(request, threshold_id):
    """Mengedit threshold config"""
    
    if request.method == 'POST':
        try:
            threshold = ThresholdConfig.objects.get(id=threshold_id)
            
            threshold.alert_type = request.POST.get('alert_type')
            threshold.threshold_value = int(request.POST.get('threshold_value'))
            threshold.time_window = int(request.POST.get('time_window'))
            threshold.severity = request.POST.get('severity')
            threshold.is_active = request.POST.get('is_active') == 'on'
            threshold.description = request.POST.get('description', '')
            threshold.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Threshold config berhasil diperbarui'
            })
            
        except ThresholdConfig.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Threshold config not found'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error updating data: {str(e)}'
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })
