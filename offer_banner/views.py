from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import SpecialOffer

def special_offers(request):
    offers = SpecialOffer.objects.all()
    return render(request, 'index.html', {'offers': offers})
