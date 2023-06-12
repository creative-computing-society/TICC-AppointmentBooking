from typing import Any, Optional
from django.core.management.base import BaseCommand
from slots.models import AvailableSlot

class Command(BaseCommand):
    help = "Populate the database with slots"

    def handle(self, *args: Any, **options) :
        # Input whether to delete all previous slots
        ans = input("Do you want to delete all previous slots? (y/n): ")
        if ans == 'y':
            AvailableSlot.objects.all().delete()
            print("Deleted all slots")
        
        # Input whether to create slots for next day or for next 14 days
        ans = input("Do you want to create slots for next day or for next 14 days? (1/14): ")
        if ans == '1':
            # Create slots for next day
            # run generate_slots_next_day(self): from slots\models.py AvailableSlot class 
            AvailableSlot.generate_slots_next_day()   

            print("Created slots for next day")
        elif ans == '14':
            # Create slots for next 14 days
            # run def generate_slots_14days(cls): from slots\models.py AvailableSlot class
            AvailableSlot.generate_slots_14days()
            print("Created slots for next 14 days")
        else:
            print("Invalid input")

