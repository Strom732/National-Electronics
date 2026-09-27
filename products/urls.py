from django.urls import include, path
from . import views
from django.views.generic import TemplateView



urlpatterns = [    
    path('', views.home, name='home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),  # URL for individual product details
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('contact/success/', TemplateView.as_view(template_name="contact_success.html"), name="contact_success"),
    path('tinymce/', include('tinymce.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
    path('terms_and_conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('shipping_and_returns/', views.shipping_and_returns, name='shipping_and_returns'),
 ]
