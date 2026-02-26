from django.shortcuts import render
from django.contrib.admin.sites import site
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
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

