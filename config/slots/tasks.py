from django.utils import timezone
from .models import AvailableSlot, Holiday
from celery import shared_task

@shared_task
def generate_slots():
        # Define the start and end times for each day
        start_time = timezone.datetime(2000, 1, 1, 9, 0, tzinfo=timezone.utc).time()
        end_time = timezone.datetime(2000, 1, 1, 16, 0, tzinfo=timezone.utc).time()

        # Get the current date and time
        now = timezone.now()
        today = now.date() 

        # Calculate the date for the next day
        next_day = today + timezone.timedelta(days=14)

        # Skip weekends (Saturday and Sunday) and holidays for the next day
        if next_day.weekday() >= 5 or Holiday.objects.filter(date=next_day).exists():
            return

        # Generate slots for the next day
        for j in range(0, 16, 2):
            start_minute = j * 30
            end_minute = (j + 1) * 30
            start_datetime = timezone.datetime.combine(next_day, start_time) + timezone.timedelta(minutes=start_minute)
            end_datetime = timezone.datetime.combine(next_day, start_time) + timezone.timedelta(minutes=end_minute)
            try:
                AvailableSlot.objects.create(date=next_day, start_time=start_datetime.time(), end_time=end_datetime.time())
                print("Slot generated for ", next_day, start_datetime.time(), end_datetime.time())
            except:
                pass


     