# urls.py
from django.urls import path
from .views import my_orders
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile_setup/', views.profile_setup, name='profile_setup'),
    path('profile/', views.profile, name='profile'),
    path('my-orders/', my_orders, name='my_orders'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('save-quotation/',views.save_quotation, name='save_quotation'),
    path( 'my-quotations/', views.my_quotations, name='my_quotations' ),
    path('create-payment/<int:quotation_id>/', views.create_payment, name='create_payment'),
    path('payment-success/<int:quotation_id>/', views.payment_success, name='payment_success'),
    path('settings/', views.user_settings, name='settings'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)