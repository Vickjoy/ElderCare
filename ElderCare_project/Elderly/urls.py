from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Default view for the root URL
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('service-booking/', views.service_booking, name='service_booking'),
    path('emergency-button/', views.emergency_button, name='emergency_button'),
    path('health-records/', views.health_records, name='health_records'),
    path('prescriptions/', views.prescriptions, name='prescriptions'),
    path('billing-section/', views.billing_section, name='billing_section'),
    path('medication-reminders/', views.medication_reminders, name='medication_reminders'),
    path('notifications/', views.notifications, name='notifications'),
    path('logout/', views.logout_confirm, name='logout'),  # Point to the logout confirmation view
    path('logout/confirm/', views.logout_confirm_action, name='logout_confirm_action'),  # Actual logout action
    path('unverified-doctor/', views.unverified_doctor, name='unverified_doctor'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('elderly-profile/<int:elderly_user_id>/', views.elderly_profile, name='elderly_profile'),
    path('acknowledge-emergency/<int:notification_id>/', views.acknowledge_emergency, name='acknowledge_emergency'),
    path('resolve-emergency/<int:notification_id>/', views.resolve_emergency, name='resolve_emergency'),
    path('monitoring-tools/', views.monitoring_tools, name='monitoring_tools'),
    path('medication-management/', views.medication_management, name='medication_management'),
    path('appointment-scheduling/', views.appointment_scheduling, name='appointment_scheduling'),
    path('assigned-elderly-users/', views.assigned_elderly_users, name='assigned_elderly_users'),  # New URL pattern
    path('emergency-alerts/', views.emergency_alerts, name='emergency_alerts'),  # New URL pattern
]