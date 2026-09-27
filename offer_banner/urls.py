from django.urls import path
from . import views

urlpatterns = [
    path('offers/', views.special_offers, name='special_offers'),
]
