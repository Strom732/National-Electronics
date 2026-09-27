from django.db import models

# Create your models here.
from django.db import models

class SpecialOffer(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='offers/')
    link = models.URLField()

    def __str__(self):
        return self.title
