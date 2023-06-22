from rest_framework import serializers, status
from .models import AvailableSlot, Holiday, Leave
from django.utils import timezone
from django.apps import apps
from django.db import transaction


Booking = apps.get_model('users', 'Booking')

class AvailableSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableSlot
        fields = ['id', 'date', 'start_time', 'end_time', 'slots_booked', 'isAvailable', 'capacity']
        


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = ['id', 'date', 'description']

    def create(self, validated_data):
        date = validated_data.get('date')

        # Check if the holiday date is in the past
        if date < timezone.now().date():
            raise serializers.ValidationError({'detail': 'Holiday date must be in the future or today.'})
        # Check if a holiday with the same date already exists
        if Holiday.objects.filter(date=date).exists():
            raise serializers.ValidationError({'detail': "A holiday with the same date already exists."})

        return super().create(validated_data)


def validate_future_date(value):
    if value < timezone.now().date():
        raise ValueError('Start date must be in the future or today.')

class LeaveSerializer(serializers.ModelSerializer):
    counsellor_email = serializers.EmailField(source='counsellor.email', read_only=True)
    class Meta:
        model = Leave
        fields = ['id', 'counsellor', 'counsellor_email', 'date', 'description', 'slots']

    @transaction.atomic()
    def update_slots_and_bookings(self, slots, date):
        """
        Update the available slots and bookings for the given date.

        This method is responsible for updating the available slots and cancelling bookings
        for a specific date when a counsellor takes leave. It sets the slot capacity to 0,
        marks the slot as unavailable, and cancels the corresponding bookings by setting
        them as inactive.

        Args:
            date (datetime.date): The date for which to update slots and bookings.

        """

        validate_future_date(date)
        for slot in slots:
            print(slot)
            print("********************")
            if slot.capacity == 2:
                # For slots with capacity 2, set capacity and bookings to 0
                slot.capacity = 0
                slot.slots_booked = 0
                slot.isAvailable = False
                # Get the bookings for the slot
                bookings = Booking.objects.filter(slot=slot)
                for booking in bookings:
                    # Send email to the student
                    # Update the booking
                    booking.is_active = False
                    booking.remarks = 'Counsellor on leave'
                    booking.save()

            elif slot.capacity == 4:
                # For slots with capacity 4, reduce capacity to 2 and cancel extra bookings
                slot.capacity = 2
                if slot.slots_booked > 2:
                    bookings = Booking.objects.filter(slot=slot)
                    k = slot.slots_booked - 2
                    for booking in bookings:
                        # Send email to the student
                        # Update the booking
                        booking.is_active = False
                        booking.remarks = 'Counsellor on leave'
                        booking.save()
                        k -= 1
                        if k == 0:
                            break

    def create(self, validated_data):


        slot_ids = validated_data.get('slots')
        slots = AvailableSlot.objects.filter(id__in=slot_ids)
        date = validated_data.get('date')
        with transaction.atomic():
            try:
                self.update_slots_and_bookings(slots, date)
            except ValueError as e: 
                raise serializers.ValidationError({'detail': str(e)})
            return super().create(validated_data)
  