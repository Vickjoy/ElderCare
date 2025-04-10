from django.urls import path
from . import views

app_name = 'elderly'  # Define the app name

urlpatterns = [
    path('', views.home, name='home'),  # Default view for the root URL
    path('login/', views.user_login, name='user_login'),  # Ensure this line is correct
    path('register/', views.user_register, name='user_register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('service-booking/', views.service_booking, name='service_booking'),
    path('emergency-button/', views.emergency_button, name='emergency_button'),  # Ensure this line is correct
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
    path('assigned-elderly-users/', views.assigned_elderly_users, name='assigned_elderly_users'),
    path('emergency-alerts/', views.emergency_alerts, name='emergency_alerts'),
    path('view-requests/', views.view_requests, name='view_requests'),
    path('accept-request/<int:request_id>/', views.accept_request, name='accept_request'),
    path('reject-request/<int:request_id>/', views.reject_request, name='reject_request'),
    path('access-health-records/<int:elderly_user_id>/', views.access_health_records, name='access_health_records'),
    path('record-observations/<int:request_id>/', views.record_observations, name='record_observations'),
    path('issue-prescriptions/<int:request_id>/', views.issue_prescriptions, name='issue_prescriptions'),
    path('specify-service-cost/<int:request_id>/', views.specify_service_cost, name='specify_service_cost'),
    path('complete-session/<int:request_id>/', views.complete_session, name='complete_session'),
    path('verify-doctor/<int:doctor_id>/', views.verify_doctor, name='verify_doctor'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('generate-reports/', views.generate_reports, name='generate_reports'),
    path('system-settings/', views.system_settings, name='system_settings'),
    path('mark-prescription-completed/<int:prescription_id>/', views.mark_prescription_completed, name='mark_prescription_completed'),
    path('send-medication-reminder/<int:elderly_user_id>/', views.send_medication_reminder, name='send_medication_reminder'),
    path('schedule-appointment/<int:request_id>/', views.schedule_appointment, name='schedule_appointment'),
]