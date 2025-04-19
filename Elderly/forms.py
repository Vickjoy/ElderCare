from django import forms
from .models import (
    CustomUser, ElderlyUser, Caregiver, Doctor, Admin, HealthRecord, Observation, Prescription, Billing
)

class UserRegistrationForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, required=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password1', 'password2', 'role']

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            if len(password1) < 8:
                raise forms.ValidationError("Your password must contain at least 8 characters.")
            if password1.isdigit():
                raise forms.ValidationError("Your password can’t be entirely numeric.")
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two password fields didn't match.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = ElderlyUser
        fields = ['first_name', 'last_name', 'gender', 'address', 'emergency_contact']

class CaregiverProfileForm(forms.ModelForm):
    class Meta:
        model = Caregiver
        fields = ['first_name', 'last_name', 'relationship', 'contact_number']

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['first_name', 'last_name', 'specialization', 'license_number']

class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = Admin
        fields = ['permissions']

class HealthRecordForm(forms.ModelForm):
    class Meta:
        model = HealthRecord
        fields = [
            'medical_history',
            'current_medications',
            'allergies',
            'blood_pressure',
            'heart_rate',
            'sugar_levels',
        ]
        widgets = {
            'medical_history': forms.Textarea(attrs={'rows': 4}),
            'current_medications': forms.Textarea(attrs={'rows': 4}),
            'allergies': forms.Textarea(attrs={'rows': 4}),
        }

class ObservationForm(forms.ModelForm):
    class Meta:
        model = Observation
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['medication_name', 'dosage', 'duration', 'additional_notes']
        widgets = {
            'medication_name': forms.TextInput(attrs={'placeholder': 'Medication Name'}),
            'dosage': forms.TextInput(attrs={'placeholder': 'Dosage'}),
            'duration': forms.TextInput(attrs={'placeholder': 'Duration'}),
            'additional_notes': forms.Textarea(attrs={'rows': 4}),
        }

class BillingForm(forms.ModelForm):
    class Meta:
        model = Billing
        fields = ['service_cost', 'paybill', 'account_number']
        widgets = {
            'service_cost': forms.NumberInput(attrs={'step': '0.01'}),
            'paybill': forms.TextInput(attrs={'placeholder': 'Paybill Number'}),
            'account_number': forms.TextInput(attrs={'placeholder': 'Account Number'}),
        }