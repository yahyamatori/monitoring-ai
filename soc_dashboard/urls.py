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
]
