from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, ElderlyUser, Caregiver, Doctor, Admin

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, required=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password1', 'password2', 'role']

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = ElderlyUser
        fields = ['first_name', 'last_name', 'date_of_birth', 'gender', 'address', 'emergency_contact']

class CaregiverProfileForm(forms.ModelForm):
    class Meta:
        model = Caregiver
        fields = ['first_name', 'last_name', 'relationship', 'assigned_users']

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['first_name', 'last_name', 'specialization', 'license_number']

class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = Admin
        fields = ['permissions']

class ServiceRequestForm(forms.Form):
    specialization = forms.ChoiceField(choices=[
        ('cardiologist', 'Cardiologist'),
        ('neurologist', 'Neurologist'),
        ('geriatrician', 'Geriatrician'),
        # Add more specializations as needed
    ], required=True)

class EmergencyNotificationForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea, required=True)