# views.py
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from user_dashboard.forms import ProfileSettingsForm, ProfileSetupForm
from .models import UserProfile,Order,OrderItem,Quotation,QuotationItem
from .utils import get_google_profile_image

@login_required
def dashboard(request):
    user = request.user
    # Get or create the UserProfile for the logged-in user
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    # Get the Google profile image (if available)
    profile_image_url = get_google_profile_image(user)

    # Pass both the user profile and the Google profile image URL to the template
    return render(request, 'dashboard.html', {
        'user_profile': user_profile,
        'profile_image_url': profile_image_url
    })
 



@login_required
def profile(request):
    user = request.user
    # Get or create the UserProfile for the logged-in user
    user_profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Get the Google profile image (if available)
    profile_image_url = get_google_profile_image(user)

    # Pass both the user profile and the Google profile image URL to the template
    return render(request, 'profile.html', {
        'user_profile': user_profile,
        'profile_image_url': profile_image_url
    })

@login_required
def my_orders(request):
    user = request.user
    user_profile, created = UserProfile.objects.get_or_create(user=user)    
    
    # Order by created_at in descending order to show latest orders on top
    orders = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at')
    
    return render(request, 'my_orders.html', {
        'orders': orders,
        'user_profile': user_profile,
    })





@login_required
def wishlist(request):
    # Handle settings update logic
    return render(request, 'wishlist.html')

@login_required
def profile_setup(request):
    user = request.user

    # Ensure the user has a UserProfile
    if not hasattr(user, 'userprofile'):
        UserProfile.objects.create(user=user)

    user_profile = user.userprofile
    
    userprofile = request.user.userprofile  # Access UserProfile using the related_name
    if request.method == 'POST':
        form = ProfileSetupForm(request.POST, request.FILES, instance=userprofile)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProfileSetupForm(instance=userprofile)
    return render(request, 'profile_setup.html', {'form': form})



@login_required
def settings(request):
     return render(request, 'settings.html')



from django.shortcuts import render, redirect, get_object_or_404
from .models import Quotation, QuotationItem
from cart.models import CartItem  # Assuming CartItem stores cart products
from products.models import Product  # Assuming Product model exists
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse




@login_required
def save_quotation(request):
    if request.method == "POST":
        user = request.user
        product_id = request.POST.get("product_id")  # Check if quoting a single product
        quantity = request.POST.get("quantity", 1)  # Default quantity to 1

        # Create a new quotation
        quotation = Quotation.objects.create(user=user)

        if product_id:  
            # ✅ Quoting a SINGLE product
            product = get_object_or_404(Product, id=product_id)
            QuotationItem.objects.create(
                quotation=quotation,
                product=product,
                quantity=int(quantity),
                price=product.price
            )
        else:
            cart_items = CartItem.objects.filter(user=user)
            quotation_items = cart_items.filter(product__quotation_product=True)
            for item in quotation_items:
                QuotationItem.objects.create(
                    quotation=quotation,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

            # Clear cart after quotation
            quotation_items.delete()

        return redirect('my_quotations')
    
    return redirect('home')


import razorpay
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from decimal import Decimal
from .models import Quotation

# Razorpay Client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required
def my_quotations(request):
    # Order by creation time descending
    quotations = Quotation.objects.filter(user=request.user).prefetch_related("items__product").order_by('-created_at')

    for quotation in quotations:
        admin_total = sum(item.quantity * item.admin_price for item in quotation.items.all())
        gst = admin_total * Decimal('0.18')
        total_payable = admin_total + gst

        quotation.admin_total = admin_total
        quotation.total_payable = total_payable

    return render(request, 'my_quotations.html', {
        'quotations': quotations,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
    })

# Payment Processing View

@login_required
def create_payment(request, quotation_id):
    quotation = get_object_or_404(Quotation, id=quotation_id, user=request.user)

    admin_total = sum(item.quantity * item.admin_price for item in quotation.items.all())
    gst = admin_total * Decimal('0.18')
    total_payable = int((admin_total + gst) * 100)  # Convert to paisa

    # Create order in Razorpay
    order_data = {
        "amount": total_payable,
        "currency": "INR",
        "payment_capture": "1",
    }
    order = razorpay_client.order.create(order_data)

    return JsonResponse({
        "order_id": order["id"],
        "amount": total_payable,
        "currency": "INR",
    })

# Payment Success View
@login_required
def payment_success(request, quotation_id):
    quotation = get_object_or_404(Quotation, id=quotation_id, user=request.user)

    payment_id = request.GET.get("payment_id") or request.POST.get("payment_id")
    order_id = request.GET.get("order_id") or request.POST.get("order_id")
    signature = request.GET.get("signature") or request.POST.get("signature")

    if not payment_id or not order_id or not signature:
        return JsonResponse({"success": False, "message": "Missing payment details."}, status=400)

    # Verify with Razorpay before marking anything as paid — otherwise anyone
    # who knows a quotation_id could mark it paid without ever paying.
    try:
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature,
        })
    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({"success": False, "message": "Payment verification failed."}, status=400)

    quotation.payment_status = True
    quotation.save()
    return JsonResponse({"message": "Payment successful!"})

from django.shortcuts import render

def user_settings(request):
    return render(request, 'user_dashboard/settings.html')
