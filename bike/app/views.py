from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.response import Response

from .models import Bike, Rental, RentalHistory
from .serializers import UserSerializer, BikeSerializer, RentalSerializer, RentalHistorySerializer
from .tasks import calculate_rental_cost

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class BikeViewSet(viewsets.ModelViewSet):
    queryset = Bike.objects.all()
    serializer_class = BikeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Bike.objects.filter(status='available')
        return qs


class RentalViewSet(viewsets.ModelViewSet):
    queryset = Rental.objects.all()
    serializer_class = RentalSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        bike = serializer.validated_data['bike']

        # Проверка, что пользователь арендует только один велосипед одновременно
        if Rental.objects.filter(user=user, end_time__isnull=True).exists():
            raise serializers.ValidationError("You already have an ongoing rental.")

        # Проверка, что велосипед доступен
        if bike.status != 'available':
            raise serializers.ValidationError("Bike is not available for rent.")

        bike.status = 'rented'
        bike.save()

        serializer.save(user=user)

    @action(detail=True, methods=['post'])
    def return_bike(self, request, pk=None):
        rental = self.get_object()
        if rental.end_time is not None:
            return Response({"error": "This rental is already completed."}, status=400)

        rental.end_time = timezone.now()
        rental.save()

        # Рассчитать стоимость аренды
        calculate_rental_cost.delay(rental.id)

        return Response({"status": "Bike return initiated. Cost calculation in progress."})


class RentalHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RentalHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RentalHistory.objects.filter(user=self.request.user)
