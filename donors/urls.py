from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_donor, name='register_donor'),
    path('success/', views.register_success, name='register_success'),
    path('request/', views.submit_request, name='submit_request'),
    path('verify/', views.verify_donors_list, name='verify_donors_list'),
    path('verify/<int:donor_id>/', views.verify_donor, name='verify_donor'),
]