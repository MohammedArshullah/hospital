from django import forms
from django.contrib.auth.models import User
from .models import Patient
from .models import Doctor

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['phone', 'gender', 'address']

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = '__all__'
        widgets = {
            'photo': forms.FileInput(attrs={'accept': 'image/*'})  # Accept any image type
        }