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
    # Delete Data
    path('delete/', views.delete_data, name='delete_data'),
    path('delete/attack-logs/', views.delete_attack_logs, name='delete_attack_logs'),
    path('delete/alerts/', views.delete_alerts, name='delete_alerts'),
    path('delete/threshold-config/', views.delete_threshold_config, name='delete_threshold_config'),
    path('edit/threshold-config/<int:threshold_id>/', views.edit_threshold_config, name='edit_threshold_config'),
    # Instance Mapping
    path('instance-mapping/', views.instance_mapping_list, name='instance_mapping_list'),
    path('instance-mapping/sync/', views.sync_instances, name='sync_instances'),
    path('instance-mapping/add/', views.add_instance_mapping, name='add_instance_mapping'),
    path('instance-mapping/delete/<int:mapping_id>/', views.delete_instance_mapping, name='delete_instance_mapping'),
]
