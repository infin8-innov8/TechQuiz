from django.urls import path
from django.shortcuts import redirect # Added for redirect function
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('success/', views.success, name='success'),
    path('login/', views.login_view, name='login'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('waiting-room/', views.waiting_room, name='waiting_room'),
    path('', lambda request: redirect('register')), # Default redirect
]
