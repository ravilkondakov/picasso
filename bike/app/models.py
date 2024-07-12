from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Bike(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('rented', 'Rented')
    ]
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return self.name


class Rental(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bike = models.ForeignKey(Bike, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} rented {self.bike.name}"


class RentalHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bike = models.ForeignKey(Bike, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"History for {self.user.username}: {self.bike.name}"
