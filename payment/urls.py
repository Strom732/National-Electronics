from django.urls import path
from . import views

urlpatterns = [
    # Other URLs
    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),
    path('payment-verification/', views.payment_verification, name='payment_verification'),
    path('success/', views.success, name='success')  # Optional: Create a success page
]
