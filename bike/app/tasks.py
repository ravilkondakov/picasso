from celery import shared_task
from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist


@shared_task
def calculate_rental_cost(rental_id):
    from .models import Rental, RentalHistory
    try:
        rental = Rental.objects.get(id=rental_id)
        if rental.end_time:
            duration = (rental.end_time - rental.start_time).total_seconds() / 60
            rental.cost = Decimal(duration)
            rental.save()

            # Переместить запись в историю аренды
            RentalHistory.objects.create(
                user=rental.user,
                bike=rental.bike,
                start_time=rental.start_time,
                end_time=rental.end_time,
                cost=rental.cost
            )

            # Обновить статус велосипеда
            rental.bike.status = 'available'
            rental.bike.save()

            return rental.cost
    except ObjectDoesNotExist:
        return None
