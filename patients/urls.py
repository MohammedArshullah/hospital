from django.urls import path
from . import views
from django.views.generic import TemplateView


urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.patient_signup, name='signup'),
    path('login/', views.patient_login, name='login'),
    path('logout/', views.patient_logout, name='logout'),
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('book/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('feedback/', views.submit_feedback, name='submit_feedback'),
    path('thankyou/', TemplateView.as_view(template_name='patients/thankyou.html'), name='feedback_thankyou'),
    path('about/', views.about_us, name='about_us'),
    path('facility/', views.facility, name='facility'),
    path('cancel-appointment/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('reschedule-appointment/<int:appointment_id>/', views.reschedule_appointment, name='reschedule_appointment'),
    path('get-busy-times/<int:doctor_id>/', views.get_busy_times, name='get_busy_times'),

]
    
    





