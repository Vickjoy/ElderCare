from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *

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
            return redirect('dashboard')
        else:
            return render(request, 'elderly/login.html', {'error': 'Invalid credentials'})
    return render(request, 'elderly/login.html')

def user_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']
            user.set_password(form.cleaned_data['password1'])  # Use password1 from the form
            user.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'elderly/register.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    if user.role == 'elderly':
        return render(request, 'elderly/dashboard.html')
    elif user.role == 'caregiver':
        return render(request, 'elderly/caregiver_dashboard.html')
    elif user.role == 'doctor':
        return render(request, 'elderly/doctor_dashboard.html')
    elif user.role == 'admin':
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
            form = UserProfileForm(instance=user.elderlyuser)
    elif user.role == 'caregiver':
        if request.method == 'POST':
            form = CaregiverProfileForm(request.POST, instance=user.caregiver)
            if form.is_valid():
                form.save()
                return redirect('dashboard')
        else:
            form = CaregiverProfileForm(instance=user.caregiver)
    elif user.role == 'doctor':
        if request.method == 'POST':
            form = DoctorProfileForm(request.POST, instance=user.doctor)
            if form.is_valid():
                form.save()
                return redirect('dashboard')
        else:
            form = DoctorProfileForm(instance=user.doctor)
    elif user.role == 'admin':
        if request.method == 'POST':
            form = AdminProfileForm(request.POST, instance=user.admin)
            if form.is_valid():
                form.save()
                return redirect('dashboard')
        else:
            form = AdminProfileForm(instance=user.admin)
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