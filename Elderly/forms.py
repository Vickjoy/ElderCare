from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, ElderlyUser, Caregiver, Doctor, Admin

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
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
        user = super(UserRegistrationForm, self).save(commit=False)
        user.username = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = ElderlyUser
        fields = ['first_name', 'last_name', 'gender', 'address', 'emergency_contact']  # Removed date_of_birth

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