import json
from django.http import JsonResponse
import razorpay
from django.conf import settings
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from products.models import Product

@login_required
@csrf_exempt
def buy_now(request, product_id):
    if request.method == "POST":
        try:
            product = Product.objects.get(id=product_id)
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

            # Ensure the price is correctly converted to paise
            amount = int(product.price * 100)  # Convert INR to paise (Razorpay requires paise)

            # Create a Razorpay order
            payment = client.order.create({
                'amount': amount,
                'currency': 'INR',
                'payment_capture': '1'
            })

            # Pass order details to the template
            return render(request, 'product_detail.html', {
                'product': product,
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'order_id': payment['id'],
                'amount': amount
            })

        except Product.DoesNotExist:
            return JsonResponse({"error": "Product not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)



        
@csrf_exempt
def payment_verification(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON data
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

            client.utility.verify_payment_signature({
                'razorpay_order_id': data['order_id'],
                'razorpay_payment_id': data['payment_id'],
                'razorpay_signature': data['signature']
            })

            return JsonResponse({'success': True})

        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'success': False})

    return JsonResponse({'error': 'Invalid request'}, status=400)

def success(request):
        return render(request, 'my_orders.html')
def my_orders(request):
    return render(request, 'my_orders.html')