from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from .models import ServiceRequest


def services(request):
    return render(request, 'services.html')

