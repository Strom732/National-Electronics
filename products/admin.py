from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import redirect
from django.http import HttpResponse
from django.middleware.csrf import get_token
import pandas as pd

from products.forms import ProductImageForm
from .models import Product, ProductImage, Category
from ckeditor.widgets import CKEditorWidget


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    form = ProductImageForm
    extra = 1
    max_num = 1
    min_num = 0


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'is_featured', 'quotation_product')
    search_fields = ('name', 'category__name')
    inlines = [ProductImageInline]

    def get_urls(self):
        """Extend admin URLs to include an Excel upload page."""
        urls = super().get_urls()
        custom_urls = [
            path('upload-excel/', self.admin_site.admin_view(self.upload_excel), name='upload-excel'),
        ]
        return custom_urls + urls

    def upload_excel(self, request):
        """Handle Excel file upload and render an inline HTML form if GET."""
        if request.method == "POST":
            excel_file = request.FILES.get("excel_file")
            if not excel_file:
                self.message_user(request, "No file uploaded!", level=messages.ERROR)
                return redirect("..")

            try:
                df = pd.read_excel(excel_file)  # Read Excel file
                
                # Fill NaN values with defaults
                df.fillna({
                    "Product Name": "Unnamed Product",
                    # "Base Price": 0,
                    # "Price No GST": 0,
                    "Price": 0,
                    "Description": "",
                    "Category": "Uncategorized",
                    "Featured": False,
                    "Quotation Product": False,
                    "Image URLs": ""
                }, inplace=True)

                for _, row in df.iterrows():
                    category_name = str(row["Category"]).strip()
                    category, _ = Category.objects.get_or_create(name=category_name)

                    # Convert to integer safely (avoiding NaN issues)
                    # base_price = int(row["Base Price"]) if pd.notna(row["Base Price"]) else 0
                    # price_nogst = int(row["Price No GST"]) if pd.notna(row["Price No GST"]) else 0
                    price = int(row["Price"]) if pd.notna(row["Price"]) else 0

                    product, created = Product.objects.get_or_create(
                       name=row["Product Name"],
                       defaults={
                        #    "base_price": base_price,
                        #    "price_nogst": price_nogst,
                           "price": price,
                           "description": row["Description"],
                           "category": category,
                           "is_featured": bool(row["Featured"]),
                           "quotation_product": bool(row["Quotation Product"]),
                       }
                    )

                    # Process Image URLs
                    image_urls = str(row["Image URLs"]).split(",")  
                    for index, image_url in enumerate(image_urls):
                        image_url = image_url.strip()
                        if not image_url:
                            continue
                        ProductImage.objects.create(
                            product=product,
                            image=image_url,
                            is_primary=(index == 0)
                        )

                self.message_user(request, "Products imported successfully!", level=messages.SUCCESS)
                return redirect("..")

            except Exception as e:
                self.message_user(request, f"Error: {str(e)}", level=messages.ERROR)
                return redirect("..")

        else:
            csrf_token = get_token(request)
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
              <title>Bulk Upload</title>
              <style>
                body {{ font-family: sans-serif; margin: 40px; }}
                h1 {{ color: #333; }}
                form {{ margin-top: 20px; }}
                .button {{
                    background-color: #007bff;
                    border: none;
                    color: white;
                    padding: 10px 20px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 16px;
                    margin: 4px 2px;
                    cursor: pointer;
                    border-radius: 4px;
                }}
              </style>
            </head>
            <body>
              <h1>Bulk Upload</h1>
              <form method="post" enctype="multipart/form-data">
                <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                <input type="file" name="excel_file" accept=".xlsx, .xls">
                <br><br>
                <button type="submit" class="button">Upload</button>
              </form>
              <p><a href="../">Back to Product List</a></p>
            </body>
            </html>
            """
            return HttpResponse(html)


admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
