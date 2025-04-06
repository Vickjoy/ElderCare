from django.contrib import admin
from .models import *

admin.site.register(CustomUser)
admin.site.register(ElderlyUser)
admin.site.register(Caregiver)
admin.site.register(Doctor)
admin.site.register(Admin)
admin.site.register(HealthRecord)
admin.site.register(ServiceRequest)
admin.site.register(Observation)
admin.site.register(Prescription)
admin.site.register(Billing)
admin.site.register(EmergencyNotification)
admin.site.register(FeedbackNotification)