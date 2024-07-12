from django.contrib import admin
from .models import User, Bike, Rental, RentalHistory

admin.site.register(User)
admin.site.register(Bike)
admin.site.register(Rental)
admin.site.register(RentalHistory)
