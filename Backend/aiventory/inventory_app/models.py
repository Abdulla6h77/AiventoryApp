from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField()
    category = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return self.name

# Create your models here.
