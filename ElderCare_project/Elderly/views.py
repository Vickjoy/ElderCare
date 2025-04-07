from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import (
    CustomUser, ElderlyUser, Caregiver, Doctor, Admin, EmergencyNotification, FeedbackNotification,
    HealthRecord, ServiceRequest, Prescription, Billing
)
from .forms import (
    UserRegistrationForm, UserProfileForm, CaregiverProfileForm, DoctorProfileForm, AdminProfileForm
)

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('login')

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            # Redirect based on user role and profile completion
            if user.role == 'elderly':
                if not hasattr(user, 'elderlyuser') or not user.elderlyuser.first_name:
                    return redirect('profile')
                return redirect('dashboard')
            elif user.role == 'caregiver':
                if not hasattr(user, 'caregiver') or not user.caregiver.first_name:
                    return redirect('profile')
                return redirect('dashboard')
            elif user.role == 'doctor':
                if not hasattr(user, 'doctor') or not user.doctor.first_name:
                    return redirect('profile')
                if user.doctor.verified_status:
                    return redirect('dashboard')
                else:
                    return render(request, 'elderly/unverified_doctor.html')
            elif user.role == 'admin':
                if not hasattr(user, 'admin') or not user.admin.permissions:
                    return redirect('profile')
                return redirect('admin_dashboard')
        else:
            return render(request, 'elderly/login.html', {'error': 'Invalid credentials'})
    return render(request, 'elderly/login.html')

def user_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']
            user.set_password(form.cleaned_data['password1'])
            user.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'elderly/register.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    if user.role == 'elderly':
        if not hasattr(user, 'elderlyuser') or not user.elderlyuser.first_name:
            return redirect('profile')
        return render(request, 'elderly/dashboard.html')
    elif user.role == 'caregiver':
        if not hasattr(user, 'caregiver') or not user.caregiver.first_name:
            return redirect('profile')
        
        # Ensure assigned_users is not None
        assigned_users = user.caregiver.assigned_users if user.caregiver.assigned_users else []
        
        emergency_notifications = EmergencyNotification.objects.filter(
            elderly_user__id__in=assigned_users,
            status='sent'
        ).order_by('-timestamp')
        
        feedback_notifications = FeedbackNotification.objects.filter(
            notification__elderly_user__id__in=assigned_users
        ).order_by('-timestamp')
        
        return render(request, 'elderly/caregiver_dashboard.html', {
            'assigned_users': assigned_users,
            'emergency_notifications': emergency_notifications,
            'feedback_notifications': feedback_notifications
        })
    elif user.role == 'doctor':
        if not hasattr(user, 'doctor') or not user.doctor.first_name:
            return redirect('profile')
        if not user.doctor.verified_status:
            return render(request, 'elderly/unverified_doctor.html')
        return render(request, 'elderly/doctor_dashboard.html')
    elif user.role == 'admin':
        if not hasattr(user, 'admin') or not user.admin.permissions:
            return redirect('profile')
        return render(request, 'elderly/admin_dashboard.html')
    return redirect('login')

@login_required
def profile(request):
    user = request.user
    if user.role == 'elderly':
        if request.method == 'POST':
            form = UserProfileForm(request.POST, instance=user.elderlyuser)
            if form.is_valid():
                form.save()
                return redirect('dashboard')
        else:
            if hasattr(user, 'elderlyuser'):
                form = UserProfileForm(instance=user.elderlyuser)
            else:
                ElderlyUser.objects.create(user=user)
                form = UserProfileForm()
    elif user.role == 'caregiver':
        if request.method == 'POST':
            form = CaregiverProfileForm(request.POST, instance=user.caregiver)
            if form.is_valid():
                form.save()
                return redirect('dashboard')
        else:
            if hasattr(user, 'caregiver'):
                form = CaregiverProfileForm(instance=user.caregiver)
            else:
                Caregiver.objects.create(user=user, assigned_users=[])
                form = CaregiverProfileForm()
    elif user.role == 'doctor':
        if request.method == 'POST':
            form = DoctorProfileForm(request.POST, instance=user.doctor)
            if form.is_valid():
                form.save()
                return redirect('dashboard')
        else:
            if hasattr(user, 'doctor'):
                form = DoctorProfileForm(instance=user.doctor)
            else:
                Doctor.objects.create(user=user)
                form = DoctorProfileForm()
    elif user.role == 'admin':
        if request.method == 'POST':
            form = AdminProfileForm(request.POST, instance=user.admin)
            if form.is_valid():
                form.save()
                return redirect('dashboard')
        else:
            if hasattr(user, 'admin'):
                form = AdminProfileForm(instance=user.admin)
            else:
                Admin.objects.create(user=user)
                form = AdminProfileForm()
    return render(request, 'elderly/profile.html', {'form': form})

@login_required
def service_booking(request):
    if request.method == 'POST':
        specialization = request.POST.get('specialization')
        ServiceRequest.objects.create(elderly_user=request.user.elderlyuser, specialization=specialization, status='pending')
        return redirect('dashboard')
    return render(request, 'elderly/service_booking.html')

@login_required
def emergency_button(request):
    if request.user.role == 'elderly':
        caregiver = Caregiver.objects.first()  # Simplified for demonstration
        if caregiver:
            EmergencyNotification.objects.create(
                elderly_user=request.user.elderlyuser,
                caregiver=caregiver,
                status='sent'
            )
        return redirect('dashboard')
    return redirect('dashboard')

@login_required
def health_records(request):
    if request.user.role == 'elderly':
        records = HealthRecord.objects.filter(elderly_user=request.user.elderlyuser)
        return render(request, 'elderly/health_records.html', {'records': records})
    elif request.user.role == 'doctor':
        elderly_user_id = request.GET.get('elderly_user_id')
        if elderly_user_id:
            elderly_user = get_object_or_404(ElderlyUser, id=elderly_user_id)
            records = HealthRecord.objects.filter(elderly_user=elderly_user)
            return render(request, 'elderly/health_records.html', {'records': records, 'elderly_user': elderly_user})
    return redirect('dashboard')

@login_required
def prescriptions(request):
    if request.user.role == 'elderly':
        prescriptions = Prescription.objects.filter(request__elderly_user=request.user.elderlyuser)
        return render(request, 'elderly/prescriptions.html', {'prescriptions': prescriptions})
    elif request.user.role == 'caregiver':
        return redirect('medication_management')
    return redirect('dashboard')

@login_required
def billing_section(request):
    if request.user.role == 'elderly':
        bills = Billing.objects.filter(request__elderly_user=request.user.elderlyuser)
        return render(request, 'elderly/billing_section.html', {'bills': bills})
    return redirect('dashboard')

@login_required
def medication_reminders(request):
    if request.user.role == 'elderly':
        return render(request, 'elderly/medication_reminders.html')
    elif request.user.role == 'caregiver':
        return redirect('medication_management')
    return redirect('dashboard')

@login_required
def notifications(request):
    if request.user.role == 'elderly':
        notifications = FeedbackNotification.objects.filter(notification__elderly_user=request.user.elderlyuser)
        return render(request, 'elderly/notifications.html', {'notifications': notifications})
    elif request.user.role == 'caregiver':
        return redirect('notifications')
    return redirect('dashboard')

@login_required
def logout_confirm(request):
    return render(request, 'elderly/logout_confirm.html')

def logout_confirm_action(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    return redirect('logout_confirm')

@login_required
def unverified_doctor(request):
    return render(request, 'elderly/unverified_doctor.html')

@login_required
def admin_dashboard(request):
    if request.user.role == 'admin':
        if not hasattr(user, 'admin') or not user.admin.permissions:
            return redirect('profile')
        doctors = Doctor.objects.filter(verified_status=False)
        return render(request, 'elderly/admin_dashboard.html', {'doctors': doctors})
    return redirect('dashboard')

@login_required
def elderly_profile(request, elderly_user_id):
    try:
        elderly_user = ElderlyUser.objects.get(id=elderly_user_id)
        return render(request, 'elderly/elderly_profile.html', {'elderly_user': elderly_user})
    except ElderlyUser.DoesNotExist:
        return redirect('dashboard')

@login_required
def acknowledge_emergency(request, notification_id):
    try:
        notification = EmergencyNotification.objects.get(id=notification_id)
        if notification.caregiver == request.user.caregiver:
            notification.status = 'acknowledged'
            notification.save()
            FeedbackNotification.objects.create(
                notification=notification,
                message="Help is on the way!",
                status='sent'
            )
            return redirect('dashboard')
    except EmergencyNotification.DoesNotExist:
        pass
    return redirect('dashboard')

@login_required
def resolve_emergency(request, notification_id):
    try:
        notification = EmergencyNotification.objects.get(id=notification_id)
        if notification.caregiver == request.user.caregiver:
            notification.status = 'resolved'
            notification.save()
            return redirect('dashboard')
    except EmergencyNotification.DoesNotExist:
        pass
    return redirect('dashboard')

@login_required
def monitoring_tools(request):
    if request.user.role == 'caregiver':
        # Ensure assigned_users is not None
        assigned_users = request.user.caregiver.assigned_users if request.user.caregiver.assigned_users else []
        
        # Fetch health records for assigned elderly users
        health_records = {}
        for user_id in assigned_users:
            elderly_user = get_object_or_404(ElderlyUser, id=user_id)
            records = HealthRecord.objects.filter(elderly_user=elderly_user).order_by('-last_updated')
            health_records[elderly_user] = records
        
        # Estimated ranges for health metrics
        health_metrics_ranges = {
            'blood_pressure': {'low': (90, 120), 'high': (140, 180)},
            'heart_rate': {'low': 60, 'high': 100},
            'sugar_levels': {'low': 70, 'high': 110},  # Fasting glucose levels
        }
        
        return render(request, 'elderly/monitoring_tools.html', {
            'health_records': health_records,
            'health_metrics_ranges': health_metrics_ranges
        })
    return redirect('dashboard')

@login_required
def medication_management(request):
    if request.user.role == 'caregiver':
        # Ensure assigned_users is not None
        assigned_users = request.user.caregiver.assigned_users if request.user.caregiver.assigned_users else []
        
        # Fetch prescriptions for assigned elderly users
        prescriptions = {}
        for user_id in assigned_users:
            elderly_user = get_object_or_404(ElderlyUser, id=user_id)
            user_prescriptions = Prescription.objects.filter(request__elderly_user=elderly_user)
            prescriptions[elderly_user] = user_prescriptions
        
        return render(request, 'elderly/medication_management.html', {
            'prescriptions': prescriptions
        })
    return redirect('dashboard')

@login_required
def appointment_scheduling(request):
    if request.user.role == 'caregiver':
        # Ensure assigned_users is not None
        assigned_users = request.user.caregiver.assigned_users if request.user.caregiver.assigned_users else []
        
        # Fetch service requests for assigned elderly users
        service_requests = {}
        for user_id in assigned_users:
            elderly_user = get_object_or_404(ElderlyUser, id=user_id)
            user_requests = ServiceRequest.objects.filter(elderly_user=elderly_user, status='pending')
            service_requests[elderly_user] = user_requests
        
        return render(request, 'elderly/appointment_scheduling.html', {
            'service_requests': service_requests
        })
    return redirect('dashboard')

@login_required
def assigned_elderly_users(request):
    if request.user.role == 'caregiver':
        # Ensure assigned_users is not None
        assigned_users = request.user.caregiver.assigned_users if request.user.caregiver.assigned_users else []
        
        # Fetch detailed profiles for assigned elderly users
        elderly_users = ElderlyUser.objects.filter(id__in=assigned_users)
        
        return render(request, 'elderly/assigned_elderly_users.html', {
            'elderly_users': elderly_users
        })
    return redirect('dashboard')

@login_required
def emergency_alerts(request):
    if request.user.role == 'caregiver':
        # Ensure assigned_users is not None
        assigned_users = request.user.caregiver.assigned_users if request.user.caregiver.assigned_users else []
        
        emergency_notifications = EmergencyNotification.objects.filter(
            elderly_user__id__in=assigned_users,
            status='sent'
        ).order_by('-timestamp')
        
        return render(request, 'elderly/emergency_alerts.html', {
            'emergency_notifications': emergency_notifications
        })
    return redirect('dashboard')