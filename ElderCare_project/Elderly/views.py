from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Billing, CustomUser, ElderlyUser, Caregiver, Doctor, Admin, EmergencyNotification, FeedbackNotification, HealthRecord, Prescription, ServiceRequest
from .forms import UserRegistrationForm, UserProfileForm, CaregiverProfileForm, DoctorProfileForm, AdminProfileForm

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
        assigned_users = ElderlyUser.objects.filter(id__in=user.caregiver.assigned_users)
        return render(request, 'elderly/caregiver_dashboard.html', {'assigned_users': assigned_users})
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
                Caregiver.objects.create(user=user)
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
        EmergencyNotification.objects.create(elderly_user=request.user.elderlyuser, caregiver=caregiver, status='sent')
        return redirect('dashboard')
    return redirect('dashboard')

@login_required
def health_records(request):
    records = HealthRecord.objects.filter(elderly_user=request.user.elderlyuser)
    return render(request, 'elderly/health_records.html', {'records': records})

@login_required
def prescriptions(request):
    prescriptions = Prescription.objects.filter(request__elderly_user=request.user.elderlyuser)
    return render(request, 'elderly/prescriptions.html', {'prescriptions': prescriptions})

@login_required
def billing_section(request):
    bills = Billing.objects.filter(request__elderly_user=request.user.elderlyuser)
    return render(request, 'elderly/billing_section.html', {'bills': bills})

@login_required
def medication_reminders(request):
    # Placeholder for medication reminders
    return render(request, 'elderly/medication_reminders.html')

@login_required
def notifications(request):
    notifications = FeedbackNotification.objects.filter(notification__elderly_user=request.user.elderlyuser)
    return render(request, 'elderly/notifications.html', {'notifications': notifications})

@login_required
def logout_confirm(request):
    return render(request, 'elderly/logout_confirm.html')

def logout_confirm_action(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    return redirect('logout_confirm')