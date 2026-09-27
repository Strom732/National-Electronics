import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, CartItem
from django.db.models import Sum
from django.contrib import messages
from user_dashboard.models import UserProfile
import razorpay
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
  # Ensure you have an Order model

logger = logging.getLogger(__name__)

# Define a function called product_list that takes in a request as a parameter
def product_list(request):
    # Get all products from the database
    products = Product.objects.all()
    # Render the index.html page and pass in the products as a context variable
    return render(request, '../Pages/index.html', {'products': products})
 
# Define a function called view_cart that takes in a request as a parameter

@login_required
def add_to_cart(request, product_id):
    user = request.user
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = CartItem.objects.get_or_create(product=product, user=user)
    cart_item.quantity += 1
    cart_item.save()

    messages.success(request, 'Item added to cart!')
    return redirect(request.META.get('HTTP_REFERER', 'home'))

    
@login_required
def remove_one_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    
    messages.success(request, 'Cart Updated')    

    return redirect('cart:view_cart')


@login_required
def remove_all_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    messages.success(request, 'Cart Updated')

    return redirect('cart:view_cart')
 

@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user).order_by('id')

    quotation_items = cart_items.filter(product__quotation_product=True)
    normal_items = cart_items.exclude(product__quotation_product=True)

    tpwg = sum((item.product.price or 0) * (item.quantity or 0) for item in cart_items)
    total_price = sum((item.product.price or 0) * (item.quantity or 0) for item in cart_items)
    cart_items_count = cart_items.aggregate(Sum('quantity'))['quantity__sum'] or 0
    item_total = [(item, (item.product.price or 0) * (item.quantity or 0)) for item in cart_items]

    # Assign custom attributes to each item
    for item in cart_items:
        item.amount = (item.product.price or 0) * (item.quantity or 0)
        item.total = (item.quantity or 0) * (item.product.price or 0)
    
    for items in normal_items:
        items.amount = (items.product.price or 0) * (items.quantity or 0)
    # If you need a separate 'item_amount', define it explicitly:
    first_item_amount = cart_items.first().amount if cart_items.exists() else 0

    context = {
        'normal_items': normal_items,
        'cart_items': cart_items,
        'tpwg': tpwg,
        'total_price': total_price,
        'cart_items_count': cart_items_count,
        'item_total': item_total,
        'item_amount': first_item_amount,  # now explicitly defined
        'quotation_items': quotation_items,

    }

    return render(request, '../Pages/cart.html', context)


@login_required
def add_one_to_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.quantity += 1
    cart_item.save()
    messages.success(request, 'Cart Updated')

    return redirect('cart:view_cart')

@login_required
def checkout(request):
    user = request.user
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    product_id = request.GET.get('product_id', None)

    if product_id:
        product = get_object_or_404(Product, id=product_id)
        checkout_items = [{'product': product, 'quantity': 1, 'total_price': product.price}]
        total_price = product.price
        amt = product.price * 1
        # Store the product id in session to indicate single product checkout
        request.session['single_product_checkout'] = product_id
    else:
        cart_items = CartItem.objects.filter(user=request.user)
        normal_items = cart_items.exclude(product__quotation_product=True)
        checkout_items = [{
            'product': item.product,
            'quantity': item.quantity,
            'total_price': item.product.price * item.quantity,
            'amt': item.product.price * item.quantity
        } for item in normal_items]
        total_price = sum(item['total_price'] for item in checkout_items)
        amt = sum(item['amt'] for item in checkout_items)

    if not total_price or total_price <= 0:
        messages.info(request, 'Your cart is empty.')
        return redirect('cart:view_cart')

    # Initialize Razorpay Client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # Create Razorpay Order
    order_data = {
        "amount": int(total_price * 100),  # Convert to paise
        "currency": "INR",
        "receipt": f"order_{user.id}",
        "payment_capture": 1,  # Auto-capture payment
    }
    razorpay_order = client.order.create(data=order_data)
    
    return render(request, 'checkout.html', {
        'user_profile': user_profile,
        'checkout_items': checkout_items,
        'total_price': total_price,
        'razorpay_order_id': razorpay_order["id"],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amt': amt,
    })



from user_dashboard.models import Order, OrderItem
from products.models import Product  # Assuming your Product model is here

@login_required
def payment_success(request):
    user = request.user
    payment_id = request.GET.get("payment_id")
    order_id = request.GET.get("order_id")
    signature = request.GET.get("signature")

    logger.info(f"payment_success called: user={user}, payment_id={payment_id}, order_id={order_id}")

    if not payment_id or not order_id or not signature:
        logger.warning(f"payment_success missing params: user={user}, payment_id={payment_id}, order_id={order_id}, signature_present={bool(signature)}")
        messages.error(request, 'Payment could not be verified.')
        return redirect('home')

    # Verify the payment with Razorpay before creating any order.
    # Without this check, anyone could hit this URL with made-up IDs
    # and get an order created without ever paying.
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature,
        })
    except razorpay.errors.SignatureVerificationError:
        logger.error(f"payment_success signature verification FAILED: user={user}, payment_id={payment_id}, order_id={order_id}")
        messages.error(request, 'Payment verification failed.')
        return redirect('home')

    # Avoid creating a duplicate order if this page is reloaded/revisited
    if Order.objects.filter(payment_id=payment_id).exists():
        existing_order = Order.objects.get(payment_id=payment_id)
        return render(request, 'payment_success.html', {
            'order': existing_order,
            'payment_id': payment_id,
            'order_id': order_id,
        })

    # "Buy Now" checks out a single product directly without ever adding
    # a CartItem, so it needs its own branch here — otherwise the cart-items
    # lookup below finds nothing and the order silently never gets created.
    single_product_id = request.session.get('single_product_checkout')

    if single_product_id:
        product = get_object_or_404(Product, id=single_product_id)
        total_price = product.price

        order = Order.objects.create(
            user=user,
            payment_id=payment_id,
            order_id=order_id,
            total_price=total_price
        )
        OrderItem.objects.create(
            order=order,
            product=product.name,
            quantity=1,
            price=product.price
        )

        del request.session['single_product_checkout']

        return render(request, 'payment_success.html', {
            'order': order,
            'payment_id': payment_id,
            'order_id': order_id,
        })

    # Process only normal (non-quotation) products
    cart_items = CartItem.objects.filter(user=user, product__quotation_product=False)

    if not cart_items.exists():
        logger.error(f"payment_success: PAID but no matching cart items found! user={user}, payment_id={payment_id}, order_id={order_id}. Payment was verified but no order could be created.")
        messages.error(request, f'Your payment was successful (ID: {payment_id}) but we could not automatically create your order. Please contact support with this payment ID.')
        return redirect('home')

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    # Create Order
    order = Order.objects.create(
        user=user,
        payment_id=payment_id,
        order_id=order_id,
        total_price=total_price
    )

    # Create Order Items
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product.name,
            quantity=item.quantity,
            price=item.product.price
        )

    # Delete only the normal items from the cart
    cart_items.delete()

    logger.info(f"payment_success: Order #{order.id} created successfully for user={user}, payment_id={payment_id}")

    return render(request, 'payment_success.html', 
                  { 'order': order,
                    'payment_id': payment_id,
                    'order_id': order_id,
                   })





@login_required
def get_quotations(request):
    user = request.user
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    product_id = request.GET.get('product_id', None)

    if product_id:
        product = get_object_or_404(Product, id=product_id)
        quota_items = [{'product': product, 'quantity': 1, 'total_price': product.price}]
        request.session['single_product_checkout'] = product_id
    else:
        cart_items = CartItem.objects.filter(user=request.user)
        quotation_items = cart_items.filter(product__quotation_product=True)
        normal_items = cart_items.exclude(product__quotation_product=True)
        quota_items = [{'product': item.product, 'quantity': item.quantity,}
                            for item in quotation_items]

    
    return render(request, 'get_quotations.html', {
        'user_profile': user_profile,
        'quota_items': quota_items,
    })
    



