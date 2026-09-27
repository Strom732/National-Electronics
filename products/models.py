from django.db import models
from django.core.exceptions import ValidationError
from tinymce.models import HTMLField
from ckeditor.fields import RichTextField

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
     
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return "/static/img/default_category.jpg"  # Path to your default image

class Product(models.Model):
    name = models.CharField(max_length=255)  # Increased from 100 to 255
    # description = HTMLField(blank=True, null=True) # Use TextField for long descriptions
    description = RichTextField(config_name='default')
    # base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # price_nogst = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_featured = models.BooleanField(default=False)
    quotation_product = models.BooleanField(default=False)
    popularity = models.PositiveIntegerField(default=0)  # used by the shop page's "Popularity" sort

    # def save(self, *args, **kwargs):
    #     # Calculate GST-inclusive price only if price_nogst is provided
    #     if self.price_nogst:
    #         self.price = round(self.price_nogst * 1.18)

    #     super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def primary_image(self):
        """Return the primary image URL or fallback to first available image."""
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary.image.url
        elif self.images.exists():
            return self.images.first().image.url
        return "/static/img/default_product.jpg"  # Default placeholder image

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='products/')
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} - {'Primary' if self.is_primary else 'Secondary'}"




