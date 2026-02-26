from django.shortcuts import render
from django.contrib.admin.sites import site
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta, datetime
from .models import AttackLog, Alert, ThresholdConfig
from django.contrib.auth import logout
from django.shortcuts import redirect

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
    return redirect('login')


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

