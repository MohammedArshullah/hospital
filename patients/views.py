from django.shortcuts import render, redirect
from .forms import UserForm, PatientForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Patient, Doctor, Appointment, Feedback
from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.views.decorators.http import require_GET
from django.contrib.messages import get_messages
from datetime import datetime, timedelta, date, time


def home(request):
    return render(request, 'patients/home.html')


def patient_signup(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        patient_form = PatientForm(request.POST)

        if user_form.is_valid() and patient_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user.password)
            user.save()

            patient = patient_form.save(commit=False)
            patient.user = user
            patient.save()

            return redirect('login')
    else:
        user_form = UserForm()
        patient_form = PatientForm()

    return render(request, 'patients/signup.html', {
        'user_form': user_form,
        'patient_form': patient_form
    })


def patient_login(request):
    list(get_messages(request))  # Clear previous messages

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('patient_dashboard')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'patients/login.html')


def patient_logout(request):
    logout(request)
    return redirect('home')


@login_required(login_url='login')
def patient_dashboard(request):
    patient = Patient.objects.get(user=request.user)
    return render(request, 'patients/dashboard.html', {'patient': patient})


@login_required(login_url='login')
def doctor_list(request):
    specialization = request.GET.get('specialization', '')
    if specialization:
        doctors = Doctor.objects.filter(specialization__icontains=specialization)
    else:
        doctors = Doctor.objects.all()

    return render(request, 'patients/doctor_list.html', {
        'doctors': doctors,
        'specialization': specialization
    })

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
@login_required(login_url='login')
def book_appointment(request, doctor_id):
    patient = Patient.objects.get(user=request.user)
    doctor = Doctor.objects.get(id=doctor_id)

    selected_date = request.POST.get('date') or request.GET.get('date')
    if not selected_date:
        selected_date = datetime.today().strftime('%Y-%m-%d')

    today = datetime.today().date()
    if selected_date and datetime.strptime(selected_date, '%Y-%m-%d').date() < today:
        messages.error(request, "You cannot select a past date for appointment.")
        return redirect('book_appointment', doctor_id=doctor_id)

    existing_appointments = Appointment.objects.filter(
        doctor=doctor,
        date=selected_date
    ).order_by('time')

    if request.method == 'POST' and request.POST.get('time'):
        time_str = request.POST.get('time')
        description = request.POST.get('description')

        try:
            appointment_datetime = datetime.strptime(f"{selected_date} {time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            messages.error(request, "Invalid date or time format.")
            return redirect('book_appointment', doctor_id=doctor_id)

        start_range = (appointment_datetime - timedelta(minutes=30)).time()
        end_range = (appointment_datetime + timedelta(minutes=30)).time()

        conflict = Appointment.objects.filter(
            doctor=doctor,
            date=selected_date,
            time__gte=start_range,
            time__lte=end_range
        ).exists()

        if conflict:
            messages.error(request, "This doctor already has an appointment within 30 minutes of this time.")
            return redirect('book_appointment', doctor_id=doctor_id)

        Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date=selected_date,
            time=time_str,
            description=description
        )

        try:
            subject = '✅ Appointment Confirmation - QuickCare Hospital'
            from_email = 'mdarshullah821@gmail.com'
            to_email = [request.user.email]

            context = {
                'patient_name': request.user.first_name or request.user.username,
                'doctor_name': doctor.name,
                'date': selected_date,
                'time': time_str,
                'hospital_name': 'QuickCare Hospital'
            }

            html_content = render_to_string('patients/appointment_confirmation.html', context)
            text_content = f"Your appointment with Dr. {doctor.name} on {selected_date} at {time_str} is confirmed."

            email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
            email.attach_alternative(html_content, "text/html")
            email.send()

        except Exception as e:
            print("Email sending failed:", e)

        messages.success(request, "Appointment booked successfully.")
        return redirect('my_appointments')

    return render(request, 'patients/book_appointment.html', {
        'doctor': doctor,
        'existing_appointments': existing_appointments,
        'selected_date': selected_date
    })



@login_required
@require_GET
def get_busy_times(request, doctor_id):
    date = request.GET.get('date')
    if not date:
        return JsonResponse({'error': 'Date is required'}, status=400)

    appointments = Appointment.objects.filter(doctor_id=doctor_id, date=date).order_by('time')
    busy_times = [a.time.strftime('%H:%M') for a in appointments]

    return JsonResponse({'busy_times': busy_times})


@login_required(login_url='login')
def my_appointments(request):
    patient = Patient.objects.get(user=request.user)
    now = datetime.now()

    future_appointments = Appointment.objects.filter(
        patient=patient
    ).filter(
        date__gt=now.date()
    ) | Appointment.objects.filter(
        patient=patient,
        date=now.date(),
        time__gte=now.time()
    )

    future_appointments = future_appointments.order_by('date', 'time')

    return render(request, 'patients/my_appointments.html', {'appointments': future_appointments})


@login_required(login_url='login')
def submit_feedback(request):
    patient = Patient.objects.get(user=request.user)

    if request.method == 'POST':
        message = request.POST.get('message')
        Feedback.objects.create(patient=patient, message=message)
        return redirect('feedback_thankyou')

    return render(request, 'patients/feedback.html')


def about_us(request):
    return render(request, 'patients/about_us.html')


def facility(request):
    return render(request, 'patients/facility.html')





@login_required
def cancel_appointment(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id, patient__user=request.user)
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, "Appointment cancelled successfully.")
        return redirect('my_appointments')


@login_required
def reschedule_appointment(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id, patient__user=request.user)

    if request.method == 'POST':
        new_date = request.POST.get('date')
        new_time = request.POST.get('time')

        appointment.date = new_date
        appointment.time = new_time
        appointment.save()
        messages.success(request, "Appointment rescheduled successfully.")
        return redirect('my_appointments')

    return render(request, 'patients/reschedule_appointment.html', {'appointment': appointment})
