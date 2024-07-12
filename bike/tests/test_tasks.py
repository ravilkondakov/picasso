from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

import sys

sys.path.append("..")
from app.tasks import calculate_rental_cost
from app.models import Rental, Bike, RentalHistory

User = get_user_model()


@pytest.mark.django_db
def test_calculate_rental_cost():
    user = User.objects.create_user(username='testuser', password='testpass')
    bike = Bike.objects.create(name='Test Bike', status='rented')
    rental = Rental.objects.create(user=user, bike=bike, start_time=timezone.now() - timedelta(minutes=60))

    rental.end_time = timezone.now()
    rental.save()

    result = calculate_rental_cost(rental.id)

    rental.refresh_from_db()
    bike.refresh_from_db()
    assert rental.cost is not None
    assert bike.status == 'available'
    assert RentalHistory.objects.filter(user=user, bike=bike).exists()
