from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import (
    CustomUser, ElderlyUser, Caregiver, Doctor, Admin, EmergencyNotification, FeedbackNotification,
    HealthRecord, Observation, ServiceRequest, Prescription, Billing
)
from .forms import (
    UserRegistrationForm, UserProfileForm, CaregiverProfileForm, DoctorProfileForm, AdminProfileForm,
    HealthRecordForm, ObservationForm, PrescriptionForm, BillingForm
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
                    return redirect('elderly:doctor_dashboard')
                else:
                    return render(request, 'elderly/unverified_doctor.html')
            elif user.role == 'admin':
                # Admins do not need to complete their profile
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
        # Ensure default health record exists
        health_record, created = HealthRecord.objects.get_or_create(elderly_user=user.elderlyuser)
        if created:
            health_record.save()
        # Get the latest service request status
        request_status = None
        latest_request = ServiceRequest.objects.filter(elderly_user=user.elderlyuser).order_by('-timestamp').first()
        if latest_request:
            request_status = latest_request.status
        return render(request, 'elderly/dashboard.html', {'request_status': request_status})
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
        return redirect('elderly:doctor_dashboard')
    elif user.role == 'admin':
        return redirect('elderly:admin_dashboard')
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
        # Admins do not need to complete their profile
        return redirect('elderly:admin_dashboard')
    return render(request, 'elderly/profile.html', {'form': form})

@login_required
def service_booking(request):
    if request.method == 'POST':
        specialization = request.POST.get('specialization')
        ServiceRequest.objects.create(
            elderly_user=request.user.elderlyuser,
            specialization=specialization,
            status='pending'
        )
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
        health_record, created = HealthRecord.objects.get_or_create(elderly_user=request.user.elderlyuser)
        if request.method == 'POST':
            form = HealthRecordForm(request.POST, instance=health_record)
            if form.is_valid():
                form.save()
                return redirect('elderly:health_records')
        else:
            form = HealthRecordForm(instance=health_record)
        return render(request, 'elderly/health_records.html', {'form': form, 'health_record': health_record})
    elif request.user.role == 'doctor':
        elderly_user_id = request.GET.get('elderly_user_id')
        if elderly_user_id:
            elderly_user = get_object_or_404(ElderlyUser, id=elderly_user_id)
            health_record, created = HealthRecord.objects.get_or_create(elderly_user=elderly_user)
            if created:
                health_record.save()
            
            # Fetch the current accepted service request for the elderly user
            service_request = ServiceRequest.objects.filter(
                elderly_user=elderly_user,
                status='accepted',
                doctor=request.user.doctor
            ).first()
            
            if not service_request:
                return render(request, 'elderly/access_health_records.html', {
                    'health_record': health_record,
                    'elderly_user': elderly_user,
                    'observations': [],
                    'prescriptions': [],
                    'billing': None,
                    'request_id': None,  # Pass None if no request is found
                })
            
            if request.method == 'POST':
                form = HealthRecordForm(request.POST, instance=health_record)
                if form.is_valid():
                    form.save()
                    return redirect('elderly:access_health_records', elderly_user_id=elderly_user_id)
            
            observations = Observation.objects.filter(request=service_request).order_by('-timestamp')
            prescriptions = Prescription.objects.filter(request=service_request).order_by('-request__timestamp')
            billing = Billing.objects.filter(request=service_request).order_by('-timestamp').first()
            
            return render(request, 'elderly/access_health_records.html', {
                'health_record': health_record,
                'elderly_user': elderly_user,
                'observations': observations,
                'prescriptions': prescriptions,
                'billing': billing,
                'request_id': service_request.id,  # Pass the request_id
            })
    return redirect('elderly:dashboard')

@login_required
def prescriptions(request):
    if request.user.role == 'elderly':
        prescriptions = Prescription.objects.filter(request__elderly_user=request.user.elderlyuser, request__status='accepted')
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
        notifications = FeedbackNotification.objects.filter(notification__elderly_user=request.user.elderlyuser, status='sent')
        return render(request, 'elderly/medication_reminders.html', {'notifications': notifications})
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
        # Fetch unverified doctors
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
        if not hasattr(request.user, 'doctor') or not request.user.doctor.first_name:
            return redirect('elderly:profile')
        if not request.user.doctor.verified_status:
            return render(request, 'elderly/unverified_doctor.html')
        pending_requests = ServiceRequest.objects.filter(status='pending', specialization=request.user.doctor.specialization)
        return render(request, 'elderly/view_requests.html', {'pending_requests': pending_requests})
    return redirect('elderly:dashboard')

@login_required
def accept_request(request, request_id):
    if request.user.role == 'doctor':
        try:
            service_request = ServiceRequest.objects.get(id=request_id, status='pending')
            if service_request.specialization == request.user.doctor.specialization:
                service_request.status = 'accepted'
                service_request.doctor = request.user.doctor
                service_request.save()
                # Redirect to elderly user details page
                return redirect('elderly:elderly_user_details', elderly_user_id=service_request.elderly_user.id)
            else:
                return render(request, 'elderly/view_requests.html', {
                    'pending_requests': ServiceRequest.objects.filter(status='pending', specialization=request.user.doctor.specialization),
                    'error': 'This request is not for your specialization.'
                })
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
                # Redirect back to view requests
                return redirect('elderly:view_requests')
        except ServiceRequest.DoesNotExist:
            pass
    return redirect('elderly:dashboard')

@login_required
def access_health_records(request, elderly_user_id):
    if request.user.role == 'doctor':
        try:
            elderly_user = get_object_or_404(ElderlyUser, id=elderly_user_id)
            health_record, created = HealthRecord.objects.get_or_create(elderly_user=elderly_user)
            if created:
                health_record.save()
            
            # Fetch the current accepted service request for the elderly user
            service_request = ServiceRequest.objects.filter(
                elderly_user=elderly_user,
                status='accepted',
                doctor=request.user.doctor
            ).first()
            
            if not service_request:
                return redirect('elderly:elderly_user_details', elderly_user_id=elderly_user_id)
            
            if request.method == 'POST':
                form = HealthRecordForm(request.POST, instance=health_record)
                if form.is_valid():
                    form.save()
                    return redirect('elderly:access_health_records', elderly_user_id=elderly_user_id)
            
            observations = Observation.objects.filter(request=service_request).order_by('-timestamp')
            prescriptions = Prescription.objects.filter(request=service_request).order_by('-request__timestamp')
            billing = Billing.objects.filter(request=service_request).order_by('-timestamp').first()
            
            return render(request, 'elderly/access_health_records.html', {
                'health_record': health_record,
                'elderly_user': elderly_user,
                'observations': observations,
                'prescriptions': prescriptions,
                'billing': billing,
                'request_id': service_request.id,  # Pass the request_id
            })
        except ElderlyUser.DoesNotExist:
            pass
    return redirect('elderly:dashboard')

@login_required
def record_observations(request, request_id):
    if request.user.role == 'doctor':
        try:
            service_request = get_object_or_404(ServiceRequest, id=request_id, status='accepted')
            elderly_user = service_request.elderly_user
            
            # Fetch the most recent EmergencyNotification for the elderly user
            emergency_notification = EmergencyNotification.objects.filter(
                elderly_user=elderly_user,
                status='sent'
            ).order_by('-timestamp').first()
            
            if not emergency_notification:
                # Create a new EmergencyNotification if none exists
                caregiver = Caregiver.objects.first()  # Simplified for demonstration
                if caregiver:
                    emergency_notification = EmergencyNotification.objects.create(
                        elderly_user=elderly_user,
                        caregiver=caregiver,
                        status='sent'
                    )
                else:
                    return redirect('elderly:access_health_records', elderly_user_id=elderly_user.id)
            
            if request.method == 'POST':
                form = ObservationForm(request.POST)
                if form.is_valid():
                    observation = form.save(commit=False)
                    observation.request = service_request
                    observation.save()
                    
                    # Create a feedback notification for the elderly user
                    FeedbackNotification.objects.create(
                        notification=emergency_notification,
                        message=form.cleaned_data['notes'],
                        status='sent'
                    )
                    
                    return redirect('elderly:access_health_records', elderly_user_id=elderly_user.id)
        except ServiceRequest.DoesNotExist:
            pass
    return redirect('elderly:dashboard')

@login_required
def issue_prescriptions(request, request_id):
    if request.user.role == 'doctor':
        try:
            service_request = get_object_or_404(ServiceRequest, id=request_id, status='accepted')
            if request.method == 'POST':
                form = PrescriptionForm(request.POST)
                if form.is_valid():
                    prescription = form.save(commit=False)
                    prescription.request = service_request
                    prescription.save()
                    return redirect('elderly:access_health_records', elderly_user_id=service_request.elderly_user.id)
        except ServiceRequest.DoesNotExist:
            pass
    return redirect('elderly:dashboard')

@login_required
def specify_service_cost(request, request_id):
    if request.user.role == 'doctor':
        try:
            service_request = get_object_or_404(ServiceRequest, id=request_id, status='accepted')
            if request.method == 'POST':
                form = BillingForm(request.POST)
                if form.is_valid():
                    billing = form.save(commit=False)
                    billing.request = service_request
                    billing.save()
                    return redirect('elderly:access_health_records', elderly_user_id=service_request.elderly_user.id)
        except ServiceRequest.DoesNotExist:
            pass
    return redirect('elderly:dashboard')

@login_required
def complete_session(request, request_id):
    if request.user.role == 'doctor':
        try:
            service_request = ServiceRequest.objects.get(id=request_id, status='accepted', doctor=request.user.doctor)
            service_request.status = 'completed'
            service_request.save()
            return redirect('elderly:view_requests')
        except ServiceRequest.DoesNotExist:
            pass
    return redirect('elderly:dashboard')

@login_required
def verify_doctor_list(request):
    if request.user.role == 'admin':
        doctors = Doctor.objects.filter(verified_status=False)
        return render(request, 'elderly/verify_doctor_list.html', {'doctors': doctors})
    return redirect('elderly:dashboard')

@login_required
def verify_doctor(request, doctor_id):
    if request.user.role == 'admin':
        try:
            doctor = get_object_or_404(Doctor, id=doctor_id)
            if request.method == 'POST':
                action = request.POST.get('action')
                reason = request.POST.get('reason', '')
                if action == 'accept':
                    doctor.verified_status = True
                    doctor.save()
                elif action == 'reject':
                    doctor.verified_status = False
                    doctor.save()
                return redirect('elderly:verify_doctor_list')
        except Doctor.DoesNotExist:
            pass
    return redirect('elderly:dashboard')

@login_required
def manage_users(request):
    if request.user.role == 'admin':
        if not hasattr(request.user, 'admin') or not request.user.admin.permissions:
            return redirect('elderly:profile')
        users = CustomUser.objects.all()
        return render(request, 'elderly/manage_users.html', {'users': users})
    return redirect('elderly:dashboard')

@login_required
def generate_reports(request):
    if request.user.role == 'admin':
        if not hasattr(request.user, 'admin') or not request.user.admin.permissions:
            return redirect('elderly:profile')
        # Placeholder for generating reports
        num_requests = ServiceRequest.objects.count()
        num_completed_sessions = ServiceRequest.objects.filter(status='completed').count()
        num_emergency_notifications = EmergencyNotification.objects.count()
        num_resolved_emergencies = EmergencyNotification.objects.filter(status='resolved').count()
        return render(request, 'elderly/generate_reports.html', {
            'num_requests': num_requests,
            'num_completed_sessions': num_completed_sessions,
            'num_emergency_notifications': num_emergency_notifications,
            'num_resolved_emergencies': num_resolved_emergencies
        })
    return redirect('elderly:dashboard')

@login_required
def system_settings(request):
    if request.user.role == 'admin':
        if not hasattr(request.user, 'admin') or not request.user.admin.permissions:
            return redirect('elderly:profile')
        # Placeholder for system settings
        return render(request, 'elderly/system_settings.html')
    return redirect('elderly:dashboard')

@login_required
def mark_prescription_completed(request, prescription_id):
    if request.user.role == 'caregiver':
        try:
            prescription = get_object_or_404(Prescription, id=prescription_id)
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
            elderly_user = get_object_or_404(ElderlyUser, id=elderly_user_id)
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
            service_request = get_object_or_404(ServiceRequest, id=request_id, status='pending')
            if request.method == 'POST':
                # Logic to schedule appointment
                # Placeholder for now
                service_request.status = 'scheduled'
                service_request.save()
                return redirect('elderly:appointment_scheduling')
        except ServiceRequest.DoesNotExist:
            pass
    return redirect('elderly:appointment_scheduling')

@login_required
def assign_caregiver_to_elderly(request):
    if request.user.role == 'admin':
        if request.method == 'POST':
            caregiver_id = request.POST.get('caregiver_id')
            elderly_user_id = request.POST.get('elderly_user_id')
            try:
                caregiver = get_object_or_404(Caregiver, user_id=caregiver_id)
                elderly_user = get_object_or_404(ElderlyUser, id=elderly_user_id)
                if caregiver.assigned_users:
                    caregiver.assigned_users.append(elderly_user_id)
                else:
                    caregiver.assigned_users = [elderly_user_id]
                caregiver.save()
                return redirect('elderly:assign_caregiver_to_elderly')
            except (Caregiver.DoesNotExist, ElderlyUser.DoesNotExist):
                pass
        caregivers = Caregiver.objects.all()
        elderly_users = ElderlyUser.objects.all()
        return render(request, 'elderly/assign_caregiver_to_elderly.html', {
            'caregivers': caregivers,
            'elderly_users': elderly_users
        })
    return redirect('elderly:dashboard')

@login_required
def deactivate_user(request, user_id):
    if request.user.role == 'admin':
        try:
            user = get_object_or_404(CustomUser, id=user_id)
            user.is_active = False
            user.save()
            return redirect('elderly:manage_users')
        except CustomUser.DoesNotExist:
            pass
    return redirect('elderly:manage_users')

@login_required
def pay_now(request, bill_id):
    if request.user.role == 'elderly':
        try:
            bill = get_object_or_404(Billing, id=bill_id, request__elderly_user=request.user.elderlyuser)
            if request.method == 'POST':
                bill.payment_status = 'paid'
                bill.save()
                return redirect('elderly:billing_section')
        except Billing.DoesNotExist:
            pass
    return redirect('elderly:billing_section')

@login_required
def mark_medication_taken(request, notification_id):
    if request.user.role == 'elderly':
        try:
            notification = get_object_or_404(FeedbackNotification, id=notification_id, notification__elderly_user=request.user.elderlyuser)
            if request.method == 'POST':
                notification.status = 'read'
                notification.save()
                return redirect('elderly:medication_reminders')
        except FeedbackNotification.DoesNotExist:
            pass
    return redirect('elderly:medication_reminders')

@login_required
def doctor_dashboard(request):
    if request.user.role == 'doctor':
        if not hasattr(request.user, 'doctor') or not request.user.doctor.first_name:
            return redirect('elderly:profile')
        if not request.user.doctor.verified_status:
            return render(request, 'elderly/unverified_doctor.html')
        return render(request, 'elderly/doctor_dashboard.html')
    return redirect('elderly:user_login')

@login_required
def pay_now_page(request, bill_id):
    if request.user.role == 'elderly':
        try:
            bill = get_object_or_404(Billing, id=bill_id, request__elderly_user=request.user.elderlyuser)
            if request.method == 'POST':
                # Simulate payment processing
                bill.payment_status = 'paid'
                bill.save()
                return redirect('elderly:billing_section')
            return render(request, 'elderly/pay_now.html', {'bill': bill})
        except Billing.DoesNotExist:
            pass
    return redirect('elderly:billing_section')

@login_required
def pay_now(request, bill_id):
    if request.user.role == 'elderly':
        try:
            bill = get_object_or_404(Billing, id=bill_id, request__elderly_user=request.user.elderlyuser)
            return render(request, 'elderly/pay_now_confirmation.html', {'bill': bill})
        except Billing.DoesNotExist:
            pass
    return redirect('elderly:billing_section')

@login_required
def confirm_payment(request, bill_id):
    if request.user.role == 'elderly':
        try:
            bill = get_object_or_404(Billing, id=bill_id, request__elderly_user=request.user.elderlyuser)
            if request.method == 'POST':
                # Simulate payment processing
                bill.payment_status = 'paid'
                bill.save()
                return redirect('elderly:billing_section')
        except Billing.DoesNotExist:
            pass
    return redirect('elderly:billing_section')

@login_required
def elderly_user_details(request, elderly_user_id):
    if request.user.role == 'doctor':
        try:
            elderly_user = get_object_or_404(ElderlyUser, id=elderly_user_id)
            service_request = ServiceRequest.objects.filter(
                elderly_user=elderly_user,
                status='accepted',
                doctor=request.user.doctor
            ).first()
            if service_request:
                return render(request, 'elderly/elderly_user_details.html', {
                    'elderly_user': elderly_user,
                    'request_id': service_request.id,
                })
        except ElderlyUser.DoesNotExist:
            pass
    return redirect('elderly:dashboard')