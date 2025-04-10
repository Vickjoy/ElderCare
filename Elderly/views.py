from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import (
    CustomUser, ElderlyUser, Caregiver, Doctor, Admin, EmergencyNotification, FeedbackNotification,
    HealthRecord, Observation, ServiceRequest, Prescription, Billing
)
from .forms import (
    UserRegistrationForm, UserProfileForm, CaregiverProfileForm, DoctorProfileForm, AdminProfileForm
)

def home(request):
    if request.user.is_authenticated:
        return redirect('elderly:dashboard')
    else:
        return render(request, 'elderly/home.html')  # Render a home template if needed

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
                    return redirect('elderly:profile')
                return redirect('elderly:dashboard')
            elif user.role == 'caregiver':
                if not hasattr(user, 'caregiver') or not user.caregiver.first_name:
                    return redirect('elderly:profile')
                return redirect('elderly:dashboard')
            elif user.role == 'doctor':
                if not hasattr(user, 'doctor') or not user.doctor.first_name:
                    return redirect('elderly:profile')
                if user.doctor.verified_status:
                    return redirect('elderly:dashboard')
                else:
                    return render(request, 'elderly/unverified_doctor.html')
            elif user.role == 'admin':
                if not hasattr(user, 'admin') or not user.admin.permissions:
                    return redirect('elderly:profile')
                return redirect('elderly:admin_dashboard')
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
            return redirect('elderly:user_login')
    else:
        form = UserRegistrationForm()
    return render(request, 'elderly/register.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    if user.role == 'elderly':
        if not hasattr(user, 'elderlyuser') or not user.elderlyuser.first_name:
            return redirect('elderly:profile')
        return render(request, 'elderly/dashboard.html')
    elif user.role == 'caregiver':
        if not hasattr(user, 'caregiver') or not user.caregiver.first_name:
            return redirect('elderly:profile')
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
            return redirect('elderly:profile')
        if not user.doctor.verified_status:
            return render(request, 'elderly/unverified_doctor.html')
        return render(request, 'elderly/doctor_dashboard.html')
    elif user.role == 'admin':
        if not hasattr(user, 'admin') or not user.admin.permissions:
            return redirect('elderly:profile')
        return render(request, 'elderly/admin_dashboard.html')
    return redirect('elderly:user_login')

@login_required
def profile(request):
    user = request.user
    if user.role == 'elderly':
        if request.method == 'POST':
            form = UserProfileForm(request.POST, instance=user.elderlyuser)
            if form.is_valid():
                form.save()
                return redirect('elderly:dashboard')
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
                return redirect('elderly:dashboard')
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
                return redirect('elderly:dashboard')
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
                return redirect('elderly:dashboard')
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
        return redirect('elderly:dashboard')
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
        return redirect('elderly:dashboard')
    return redirect('elderly:dashboard')

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
    return redirect('elderly:dashboard')

@login_required
def prescriptions(request):
    if request.user.role == 'elderly':
        prescriptions = Prescription.objects.filter(request__elderly_user=request.user.elderlyuser)
        return render(request, 'elderly/prescriptions.html', {'prescriptions': prescriptions})
    return redirect('elderly:dashboard')

@login_required
def billing_section(request):
    if request.user.role == 'elderly':
        bills = Billing.objects.filter(request__elderly_user=request.user.elderlyuser)
        return render(request, 'elderly/billing_section.html', {'bills': bills})
    return redirect('elderly:dashboard')

@login_required
def medication_reminders(request):
    if request.user.role == 'elderly':
        # Placeholder for medication reminders
        return render(request, 'elderly/medication_reminders.html')
    return redirect('elderly:dashboard')

@login_required
def notifications(request):
    if request.user.role == 'elderly':
        notifications = FeedbackNotification.objects.filter(notification__elderly_user=request.user.elderlyuser)
        return render(request, 'elderly/notifications.html', {'notifications': notifications})
    elif request.user.role == 'caregiver':
        notifications = FeedbackNotification.objects.filter(
            notification__elderly_user__id__in=request.user.caregiver.assigned_users
        ).order_by('-timestamp')
        return render(request, 'elderly/notifications.html', {'notifications': notifications})
    elif request.user.role == 'doctor':
        return redirect('elderly:view_requests')
    return redirect('elderly:dashboard')

@login_required
def logout_confirm(request):
    return render(request, 'elderly/logout_confirm.html')

def logout_confirm_action(request):
    if request.method == 'POST':
        logout(request)
        return redirect('elderly:home')
    return redirect('elderly:logout_confirm')

@login_required
def unverified_doctor(request):
    return render(request, 'elderly/unverified_doctor.html')

@login_required
def admin_dashboard(request):
    if request.user.role == 'admin':
        if not hasattr(user, 'admin') or not user.admin.permissions:
            return redirect('elderly:profile')
        doctors = Doctor.objects.filter(verified_status=False)
        return render(request, 'elderly/admin_dashboard.html', {'doctors': doctors})
    return redirect('elderly:dashboard')

@login_required
def elderly_profile(request, elderly_user_id):
    try:
        elderly_user = ElderlyUser.objects.get(id=elderly_user_id)
        return render(request, 'elderly/elderly_profile.html', {'elderly_user': elderly_user})
    except ElderlyUser.DoesNotExist:
        return redirect('elderly:dashboard')

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
            return redirect('elderly:dashboard')
    except EmergencyNotification.DoesNotExist:
        pass
    return redirect('elderly:dashboard')

@login_required
def resolve_emergency(request, notification_id):
    try:
        notification = EmergencyNotification.objects.get(id=notification_id)
        if notification.caregiver == request.user.caregiver:
            notification.status = 'resolved'
            notification.save()
            return redirect('elderly:dashboard')
    except EmergencyNotification.DoesNotExist:
        pass
    return redirect('elderly:dashboard')

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
    return redirect('elderly:dashboard')

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
    return redirect('elderly:dashboard')

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
    return redirect('elderly:dashboard')

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
    return redirect('elderly:dashboard')

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
    return redirect('elderly:dashboard')

@login_required
def view_requests(request):
    if request.user.role == 'doctor':
        if not hasattr(user, 'doctor') or not user.doctor.first_name:
            return redirect('elderly:profile')
        if not user.doctor.verified_status:
            return render(request, 'elderly/unverified_doctor.html')
        pending_requests = ServiceRequest.objects.filter(status='pending')
        return render(request, 'elderly/view_requests.html', {'pending_requests': pending_requests})
    return redirect('elderly:dashboard')

@login_required
def accept_request(request, request_id):
    if request.user.role == 'doctor':
        try:
            service_request = ServiceRequest.objects.get(id=request_id, status='pending')
            service_request.status = 'accepted'
            service_request.save()
            # Additional logic to handle request acceptance
            return redirect('elderly:access_health_records', elderly_user_id=service_request.elderly_user.id)
        except ServiceRequest.DoesNotExist:
            pass
    return redirect('elderly:dashboard')

@login_required
def reject_request(request, request_id):
    if request.user.role == 'doctor':
        try:
            service_request = ServiceRequest.objects.get(id=request_id, status='pending')
            if request.method == 'POST':
                reason = request.POST.get('reason', '')
                service_request.status = 'rejected'
                service_request.save()
                # Additional logic to handle request rejection
                return redirect('elderly:view_requests')
        except ServiceRequest.DoesNotExist:
            pass
    return redirect('elderly:dashboard')

@login_required
def access_health_records(request, elderly_user_id):
    if request.user.role == 'doctor':
        try:
            elderly_user = ElderlyUser.objects.get(id=elderly_user_id)
            records = HealthRecord.objects.filter(elderly_user=elderly_user)
            return render(request, 'elderly/health_records.html', {'records': records, 'elderly_user': elderly_user})
        except ElderlyUser.DoesNotExist:
            pass
    return redirect('elderly:dashboard')

@login_required
def record_observations(request, request_id):
    if request.user.role == 'doctor':
        try:
            service_request = ServiceRequest.objects.get(id=request_id, status='accepted')
            if request.method == 'POST':
                notes = request.POST.get('notes')
                Observation.objects.create(request=service_request, notes=notes)
                return redirect('elderly:access_health_records', elderly_user_id=service_request.elderly_user.id)
        except ServiceRequest.DoesNotExist:
            pass
    return redirect('elderly:dashboard')

@login_required
def issue_prescriptions(request, request_id):
    if request.user.role == 'doctor':
        try:
            service_request = ServiceRequest.objects.get(id=request_id, status='accepted')
            if request.method == 'POST':
                medication_name = request.POST.get('medication_name')
                dosage = request.POST.get('dosage')
                duration = request.POST.get('duration')
                additional_notes = request.POST.get('additional_notes')
                Prescription.objects.create(
                    request=service_request,
                    medication_name=medication_name,
                    dosage=dosage,
                    duration=duration,
                    additional_notes=additional_notes
                )
                return redirect('elderly:access_health_records', elderly_user_id=service_request.elderly_user.id)
        except ServiceRequest.DoesNotExist:
            pass
    return redirect('elderly:dashboard')

@login_required
def specify_service_cost(request, request_id):
    if request.user.role == 'doctor':
        try:
            service_request = ServiceRequest.objects.get(id=request_id, status='accepted')
            if request.method == 'POST':
                service_cost = request.POST.get('service_cost')
                Billing.objects.create(
                    request=service_request,
                    service_cost=service_cost,
                    payment_status='pending'
                )
                return redirect('elderly:access_health_records', elderly_user_id=service_request.elderly_user.id)
        except ServiceRequest.DoesNotExist:
            pass
    return redirect('elderly:dashboard')

@login_required
def complete_session(request, request_id):
    if request.user.role == 'doctor':
        try:
            service_request = ServiceRequest.objects.get(id=request_id, status='accepted')
            service_request.status = 'completed'
            service_request.save()
            return redirect('elderly:view_requests')
        except ServiceRequest.DoesNotExist:
            pass
    return redirect('elderly:dashboard')

@login_required
def verify_doctor(request, doctor_id):
    if request.user.role == 'admin':
        try:
            doctor = Doctor.objects.get(id=doctor_id)
            if request.method == 'POST':
                action = request.POST.get('action')
                reason = request.POST.get('reason', '')
                if action == 'verify':
                    doctor.verified_status = True
                    doctor.save()
                elif action == 'reject':
                    doctor.verified_status = False
                    doctor.save()
                return redirect('elderly:admin_dashboard')
        except Doctor.DoesNotExist:
            pass
    return redirect('elderly:dashboard')

@login_required
def manage_users(request):
    if request.user.role == 'admin':
        if not hasattr(user, 'admin') or not user.admin.permissions:
            return redirect('elderly:profile')
        users = CustomUser.objects.all()
        return render(request, 'elderly/manage_users.html', {'users': users})
    return redirect('elderly:dashboard')

@login_required
def generate_reports(request):
    if request.user.role == 'admin':
        if not hasattr(user, 'admin') or not user.admin.permissions:
            return redirect('elderly:profile')
        # Placeholder for generating reports
        return render(request, 'elderly/generate_reports.html')
    return redirect('elderly:dashboard')

@login_required
def system_settings(request):
    if request.user.role == 'admin':
        if not hasattr(user, 'admin') or not user.admin.permissions:
            return redirect('elderly:profile')
        # Placeholder for system settings
        return render(request, 'elderly/system_settings.html')
    return redirect('elderly:dashboard')

@login_required
def mark_prescription_completed(request, prescription_id):
    if request.user.role == 'caregiver':
        try:
            prescription = Prescription.objects.get(id=prescription_id)
            prescription.request.status = 'completed'
            prescription.request.save()
            return redirect('elderly:medication_management')
        except Prescription.DoesNotExist:
            pass
    return redirect('elderly:dashboard')

@login_required
def send_medication_reminder(request, elderly_user_id):
    if request.user.role == 'caregiver':
        try:
            elderly_user = ElderlyUser.objects.get(id=elderly_user_id)
            # Logic to send medication reminder
            # Placeholder for now
            return redirect('elderly:medication_management')
        except ElderlyUser.DoesNotExist:
            pass
    return redirect('elderly:dashboard')

@login_required
def schedule_appointment(request, request_id):
    if request.user.role == 'caregiver':
        try:
            service_request = ServiceRequest.objects.get(id=request_id, status='pending')
            if request.method == 'POST':
                # Logic to schedule appointment
                # Placeholder for now
                service_request.status = 'scheduled'
                service_request.save()
                return redirect('elderly:appointment_scheduling')
        except ServiceRequest.DoesNotExist:
            pass
    return redirect('elderly:dashboard')