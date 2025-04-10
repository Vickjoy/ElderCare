from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, ElderlyUser, Caregiver, Doctor, Admin, EmergencyNotification, FeedbackNotification,
    HealthRecord, ServiceRequest, Observation, Prescription, Billing
)

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    ordering = ('username',)
    filter_horizontal = ()

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Additional info', {'fields': ('role',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role')}
        ),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ElderlyUser)
admin.site.register(Caregiver)
admin.site.register(Doctor)
admin.site.register(Admin)
admin.site.register(EmergencyNotification)
admin.site.register(FeedbackNotification)
admin.site.register(HealthRecord)
admin.site.register(ServiceRequest)
admin.site.register(Observation)
admin.site.register(Prescription)
admin.site.register(Billing)