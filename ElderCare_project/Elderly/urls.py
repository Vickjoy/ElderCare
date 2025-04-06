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
    path('logout/confirm/', LogoutView.as_view(next_page='/'), name='logout_confirm_action'),  # Actual logout action
]