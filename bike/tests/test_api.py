import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.utils import timezone
from unittest.mock import patch
from rest_framework_simplejwt.tokens import RefreshToken

import sys

sys.path.append("..")
from app.models import Bike, Rental

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='testpass')


@pytest.fixture
def bike(db):
    return Bike.objects.create(name='Test Bike')


@pytest.fixture
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@pytest.mark.django_db
def test_register_user(api_client):
    response = api_client.post('/api/users/',
                               {'username': 'testuser2', 'password': 'testpass2', 'email': 'test2@example.com'})
    assert response.status_code == 201


@pytest.mark.django_db
def test_login_user(api_client, user):
    response = api_client.post('/api/token/', {'username': 'testuser', 'password': 'testpass'})
    assert response.status_code == 200
    assert 'access' in response.data


@pytest.mark.django_db
def test_rent_bike(api_client, user, bike, get_tokens_for_user):
    tokens = get_tokens_for_user
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access'])
    response = api_client.post('/api/rentals/', {'bike': bike.id})
    assert response.status_code == 201
    assert response.data['bike'] == bike.id
    bike.refresh_from_db()
    assert bike.status == 'rented'


@pytest.mark.django_db
@patch('app.tasks.calculate_rental_cost.delay')
def test_return_bike(mock_calculate_rental_cost, api_client, user, bike, get_tokens_for_user):
    tokens = get_tokens_for_user
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access'])
    rental = Rental.objects.create(user=user, bike=bike, start_time=timezone.now())
    response = api_client.post(f'/api/rentals/{rental.id}/return_bike/')
    assert response.status_code == 200
    mock_calculate_rental_cost.assert_called_once_with(rental.id)
