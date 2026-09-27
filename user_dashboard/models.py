from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    gst_no = models.CharField( blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True, null=True)
    
    
    def __str__(self):
        return self.user.username

from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):
    STATUS_CHOICES = [
        ('Ordered', 'Ordered'),
        ('On the Way', 'On the Way'),
        ('Delivered', 'Delivered'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    order_id = models.CharField(max_length=100)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Ordered')
    created_at = models.DateTimeField(auto_now_add=True)
    invoice = models.FileField(upload_to='invoices/', null=True, blank=True)  # Invoice upload field
    
    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product} (x{self.quantity})"





from django.db import models
from django.contrib.auth.models import User

class Quotation(models.Model):
    STATUS_CHOICES = [
        ('Ordered', 'Ordered'),
        ('On the Way', 'On the Way'),
        ('Delivered', 'Delivered'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Ordered')
    invoice = models.FileField(upload_to='invoices/', null=True, blank=True)

class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    admin_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    admin_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_payable = models.DecimalField(max_digits=10, decimal_places=2, default=0)