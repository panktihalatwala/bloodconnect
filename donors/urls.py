from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_donor, name='register_donor'),
    path('success/', views.register_success, name='register_success'),
    path('request/', views.submit_request, name='submit_request'),
    path('verify/', views.verify_donors_list, name='verify_donors_list'),
    path('verify/<int:donor_id>/', views.verify_donor, name='verify_donor'),
    path('send-otp/<int:request_id>/', views.send_otp, name='send_otp'),
    path('verify-otp/<int:request_id>/', views.verify_otp, name='verify_otp'),
    path('dashboard/', views.donor_dashboard, name='donor_dashboard'),
    path('respond/<int:match_id>/', views.respond_to_match, name='respond_to_match'),
]