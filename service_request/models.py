from django.db import models
from django.contrib.auth.models import User

class ServiceRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    condition = models.CharField(max_length=255)
    description = models.TextField()
    image1 = models.ImageField(upload_to='service_images/', blank=True, null=True)
    image2 = models.ImageField(upload_to='service_images/', blank=True, null=True)
    image3 = models.ImageField(upload_to='service_images/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.product}'
