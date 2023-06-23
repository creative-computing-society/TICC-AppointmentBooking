from typing import Any
from django.core.management.base import BaseCommand
from slots.models import AvailableSlot
from django.utils import timezone
from slots.models import Holiday

class Command(BaseCommand):
    help = "Populate the database with slots on a specific date"

    def handle(self, *args: Any, **options) :
        # Input whether to delete all previous slots
        date = input("Enter date in YYYY-MM-DD format: ")
        #verify date format
        try:
            date = timezone.datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            print("Invalid date format")
            return
        
        ans = input("Do you want to delete all previous slots on this date? (y/n): ")
        if ans == 'y':
            AvailableSlot.objects.filter(date=date).delete()
            print("Deleted all slots on", date)
        elif ans == 'n':
            pass
        else:
            print("Invalid input")
            return
        
        start_time = timezone.datetime(2000, 1, 1, 9, 0, tzinfo=timezone.utc).time()
        end_time = timezone.datetime(2000, 1, 1, 16, 0, tzinfo=timezone.utc).time()

        # Skip weekends (Saturday and Sunday) and holidays
        if date.weekday() >= 5 or Holiday.objects.filter(date=date).exists():
            ans = input("Do you want to create slots for this day - it is either a preset holiday or a weekend? (y/n):")
            if ans == 'y':
                pass
            elif ans == 'n':
                return
            else:
                print("Invalid input")
                return

        # Generate slots for the next day
        for j in range(0, 16, 1):
            start_minute = j * 30
            end_minute = (j + 1) * 30
            start_datetime = timezone.datetime.combine(date, start_time) + timezone.timedelta(minutes=start_minute)
            end_datetime = timezone.datetime.combine(date, start_time) + timezone.timedelta(minutes=end_minute)
            try:
                self.objects.create(date=date, start_time=start_datetime.time(), end_time=end_datetime.time())
            except:
                pass

