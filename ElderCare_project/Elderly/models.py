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
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10)
    address = models.TextField()
    emergency_contact = models.CharField(max_length=100)

class Caregiver(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    relationship = models.CharField(max_length=50)
    assigned_users = models.JSONField()

class Doctor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50)
    verified_status = models.BooleanField(default=False)

class Admin(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    permissions = models.JSONField()

class HealthRecord(models.Model):
    elderly_user = models.ForeignKey(ElderlyUser, on_delete=models.CASCADE)
    medical_history = models.TextField()
    current_medications = models.TextField()
    allergies = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)

class ServiceRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
    )
    elderly_user = models.ForeignKey(ElderlyUser, on_delete=models.CASCADE)
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
    caregiver = models.ForeignKey(Caregiver, on_delete=models.CASCADE)
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