from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Bike, Rental, RentalHistory

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class BikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bike
        fields = ['id', 'name', 'status']


class RentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rental
        fields = ['id', 'bike', 'start_time', 'end_time', 'cost']


class RentalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RentalHistory
        fields = ['id', 'user', 'bike', 'start_time', 'end_time', 'cost']
