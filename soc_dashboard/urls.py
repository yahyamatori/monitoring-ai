from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from dashboard import views

urlpatterns = [
    # Admin panel (tetap)
    path('admin/', admin.site.urls),
    #path('admin/logout/', auth_views.LogoutView.as_view(), name='admin_logout'),
    
    # SOC Dashboard
    path('login/', auth_views.LoginView.as_view(template_name='admin/login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),  # PAKAI VIEW CUSTOM
    path('', views.home, name='home'),
    # Attack Analysis
    path('attack-analysis/', views.attack_analysis, name='attack_analysis'),
    # IP Blocking
    path('ip-block/', views.ip_block_list, name='ip_block_list'),
    path('ip-block/add/', views.add_to_block_list, name='add_to_block_list'),
    path('ip-block/auto-add/', views.auto_add_to_block_list, name='auto_add_to_block_list'),
    path('ip-block/get-security-groups/', views.get_security_groups, name='get_security_groups'),
    path('ip-block/block/<int:block_id>/', views.block_ip, name='block_ip'),
    path('ip-block/unblock/<int:block_id>/', views.unblock_ip, name='unblock_ip'),
]
