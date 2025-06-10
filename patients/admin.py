from django.contrib import admin
from .models import Patient, Doctor, Appointment, Feedback
from .forms import DoctorForm  # custom form to accept image/* for doctor photo

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    form = DoctorForm
    list_display = ('name', 'specialization') 
admin.site.register(Patient)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'time', 'description')
    list_filter = ('doctor', 'date')
    search_fields = ('patient__user__username', 'doctor__name')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('patient', 'message', 'submitted_at')
    search_fields = ('patient__user__username', 'message')
