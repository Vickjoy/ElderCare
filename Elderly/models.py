from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('elderly', 'Elderly User'),
        ('caregiver', 'Caregiver'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

class ElderlyUser(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)

class Caregiver(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    relationship = models.CharField(max_length=50, blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    assigned_users = models.JSONField(default=list, blank=True, null=True)  # Initialize to an empty list

class Doctor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    SPECIALIZATION_CHOICES = (
        ('neurologist', 'Neurologist'),
        ('cardiologist', 'Cardiologist'),
        ('geriatrician', 'Geriatrician'),
        # Add more specializations as needed
    )
    specialization = models.CharField(max_length=100, choices=SPECIALIZATION_CHOICES, blank=True, null=True)
    license_number = models.CharField(max_length=50, blank=True, null=True)
    verified_status = models.BooleanField(default=False)

class Admin(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    permissions = models.JSONField(default=dict, blank=True, null=True)  # Initialize to an empty dictionary


            
class HealthRecord(models.Model):
    elderly_user = models.OneToOneField(ElderlyUser, on_delete=models.CASCADE)
    medical_history = models.TextField(blank=True, null=True)
    current_medications = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    blood_pressure = models.CharField(max_length=20, blank=True, null=True)  # Example format: "120/80"
    heart_rate = models.IntegerField(blank=True, null=True)
    sugar_levels = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            # Set default values for new health records
            self.current_medications = "None"
            self.allergies = "None"
            # Set default medical history based on specializations
            self.medical_history = "Default Medical History:\n"
            # Correctly access service requests through ElderlyUser
            service_requests = ServiceRequest.objects.filter(elderly_user=self.elderly_user)
            if service_requests.filter(specialization='cardiologist').exists():
                self.medical_history += "- Cardiologist: No specific issues noted.\n"
            if service_requests.filter(specialization='neurologist').exists():
                self.medical_history += "- Neurologist: No specific issues noted.\n"
            if service_requests.filter(specialization='geriatrician').exists():
                self.medical_history += "- Geriatrician: No specific issues noted.\n"
        super().save(*args, **kwargs)
        
class ServiceRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    )
    elderly_user = models.ForeignKey(ElderlyUser, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)  # Added doctor field
    specialization = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

class Observation(models.Model):
    request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE)
    notes = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Prescription(models.Model):
    request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE)
    medication_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50)
    duration = models.CharField(max_length=50)
    additional_notes = models.TextField()

class Billing(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    )
    request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE)
    service_cost = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

class EmergencyNotification(models.Model):
    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
    )
    elderly_user = models.ForeignKey(ElderlyUser, on_delete=models.CASCADE)
    caregiver = models.ForeignKey(Caregiver, on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES)

class FeedbackNotification(models.Model):
    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('read', 'Read'),
    )
    notification = models.ForeignKey(EmergencyNotification, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)