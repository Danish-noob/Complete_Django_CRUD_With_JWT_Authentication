from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('user', 'User'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return f"{self.username} ({self.role})"

class Product(models.Model):
    product_name = models.CharField(max_length=100)
    price = models.FloatField()
    quantity = models.IntegerField()
    description = models.TextField()

    def __str__(self):
        return self.product_name
