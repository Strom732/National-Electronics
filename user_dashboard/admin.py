from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(UserProfile)

from django.contrib import admin
from .models import Quotation, QuotationItem, UserProfile

class QuotationItemInline(admin.TabularInline):  # or admin.StackedInline for a different look
    model = QuotationItem
    extra = 0
    fields = ['product', 'quantity', 'admin_price', ]  # Allow admin to edit price

class QuotationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at','payment_status','status','get_user_address', 'download_invoice']
    list_filter = ['user']
    search_fields = ['user__username']
    fields = ['user', 'status', 'invoice']
    readonly_fields = ['download_invoice']
    inlines = [QuotationItemInline]  # Show items inline
    
    def download_invoice(self, obj):
        """Provide a download link for the invoice in the admin panel."""
        if obj.invoice:
            return format_html(f'<a href="{obj.invoice.url}" target="_blank">Download Invoice</a>')
        return "No Invoice Uploaded"
    
    download_invoice.short_description = "Invoice"


    def get_user_address(self, obj):
        """Fetch the address from the user's profile."""
        return obj.user.userprofile.address if hasattr(obj.user, 'userprofile') else "No address found"
    
    get_user_address.short_description = "User Address"  # Column name in admin panel

    inlines = [QuotationItemInline]

admin.site.register(Quotation, QuotationAdmin)




from .models import Order, OrderItem, UserProfile
from django.utils.html import format_html

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['product', 'quantity']  # Allow admin to edit price
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'status', 'download_invoice', 'get_user_address']
    list_editable = ['status']
    list_filter = ['user', 'status']
    search_fields = ['user__username']
    fields = ['user', 'status', 'invoice']
    readonly_fields = ['download_invoice']
    inlines = [OrderItemInline]
    

    def download_invoice(self, obj):
        """Provide a download link for the invoice in the admin panel."""
        if obj.invoice:
            return format_html(f'<a href="{obj.invoice.url}" target="_blank">Download Invoice</a>')
        return "No Invoice Uploaded"
    
    download_invoice.short_description = "Invoice"


    def get_user_address(self, obj):
        """Fetch the address from the user's profile."""
        return obj.user.userprofile.address if hasattr(obj.user, 'userprofile') else "No address found"
    
    get_user_address.short_description = "User Address"  # Column name in admin panel

    inlines = [OrderItemInline]

admin.site.register(Order, OrderAdmin)
