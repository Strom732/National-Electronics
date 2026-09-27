from django.conf import settings
from django.shortcuts import get_object_or_404, render
from .models import Product, Category
from cart.models import CartItem
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from offer_banner.models import SpecialOffer
from user_dashboard.models import UserProfile

def home(request):
    featured_products = Product.objects.filter(is_featured=True)
    products = Product.objects.all()
    categories = Category.objects.all().order_by('name')
    offers = SpecialOffer.objects.all()

    context = {
        'featured_products': featured_products,
        'offers': offers,
        'Products': products,  # Consider renaming this to 'products' for consistency
        'categories': categories
    }

    return render(request, 'index.html', context)


def product_detail(request, product_id):
    featured_products = Product.objects.filter(is_featured=True)
    """View to display the details of a specific product."""
    product = get_object_or_404(Product, id=product_id)
    user_profile = None
    if request.user.is_authenticated:
        user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    context = {
        'product': product,
        'images': product.images.all(),  # Pass all images
        "user_profile": user_profile,
        'featured_products': featured_products
    }

    return render(request, 'product_detail.html', context)



def about(request):
    return render(request, 'about.html')

from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .forms import ContactForm

def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            full_message = f"Message from {name} ({email}):\n\n{message}"
            
            send_mail(
                subject,
                full_message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_EMAIL],
            )
            
            messages.success(request, "Message sent successfully!")
            form = ContactForm()  # Clear form after successful submission
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ContactForm()
    
    return render(request, "contact.html", {"form": form})


def privacy_policy(request):
    return render(request, 'privacy-policy.html')

def shipping_and_returns(request):
    return render(request, 'shipping-and-returns.html')

def terms_and_conditions(request):
    return render(request, 'terms-and-conditions.html')