from django.db import models
from django.apps import apps
from django.db import models
from django.utils import timezone
from users.models import User

class AvailableSlot(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    slots_booked = models.IntegerField(default=0)
    capacity = models.IntegerField(default=4)
    isAvailable = models.BooleanField(default=True)
    leaves = models.ManyToManyField('Leave', through='LeaveSlot')

    def save(self, *args, **kwargs):
        if self.slots_booked >= self.capacity:
            self.isAvailable = False
        super().save(*args, **kwargs)


    @classmethod
    def generate_slots_14days(cls):
        # Define the start and end times for each day
        start_time = timezone.datetime(2000, 1, 1, 9, 0, tzinfo=timezone.utc).time()
        end_time = timezone.datetime(2000, 1, 1, 16, 0, tzinfo=timezone.utc).time()

        # Get the current date and time
        now = timezone.now()
        today = now.date() 

        # Generate slots for the next 14 days
        for i in range(14):
            # Calculate the date for the current day
            date = today + timezone.timedelta(days=i)

            # Skip weekends (Saturday and Sunday) and holidays
            if date.weekday() >= 5 or Holiday.objects.filter(date=date).exists():
                continue

            # Generate slots for the current day
            for j in range(0, 16, 1):
                start_minute = j * 30
                end_minute = (j + 1) * 30
                start_datetime = timezone.datetime.combine(date, start_time) + timezone.timedelta(minutes=start_minute)
                end_datetime = timezone.datetime.combine(date, start_time) + timezone.timedelta(minutes=end_minute)
                try:
                    cls.objects.create(date=date, start_time=start_datetime.time(), end_time=end_datetime.time())
                except:
                    pass

    @classmethod
    def generate_slots_next_day(self):
        # Define the start and end times for each day
        start_time = timezone.datetime(2000, 1, 1, 9, 0, tzinfo=timezone.utc).time()
        end_time = timezone.datetime(2000, 1, 1, 16, 0, tzinfo=timezone.utc).time()

        # Get the current date and time
        now = timezone.now()
        today = now.date() 

        # Calculate the date for the next day
        date = today + timezone.timedelta(days=1)

        # Skip weekends (Saturday and Sunday) and holidays
        if date.weekday() >= 5 or Holiday.objects.filter(date=date).exists():
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

    @classmethod
    def generate_slots(cls):
        # Define the start and end times for each day
        start_time = timezone.datetime(2000, 1, 1, 9, 0, tzinfo=timezone.utc).time()
        end_time = timezone.datetime(2000, 1, 1, 16, 0, tzinfo=timezone.utc).time()

        # Get the current date and time
        now = timezone.now()
        today = now.date() 

        # Calculate the date for the next day
        next_day = today + timezone.timedelta(days=14)


        # Skip weekends (Saturday and Sunday) and holidays for the next day
        while next_day.weekday() >= 5 or Holiday.objects.filter(date=next_day).exists():
            next_day += timezone.timedelta(days=1)

        # Generate slots for the next day
        for j in range(0, 16, 1):
            start_minute = j * 30
            end_minute = (j + 1) * 30
            start_datetime = timezone.datetime.combine(next_day, start_time) + timezone.timedelta(minutes=start_minute)
            end_datetime = timezone.datetime.combine(next_day, start_time) + timezone.timedelta(minutes=end_minute)
            try:
                cls.objects.create(date=next_day, start_time=start_datetime.time(), end_time=end_datetime.time())
                print("Slot generated for ", next_day, start_datetime.time(), end_datetime.time())
            except:
                pass

        

    def __str__(self):
        return f"{self.date} {self.start_time} "
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['date', 'start_time'], name='unique_slot')
        ]

class Holiday(models.Model):
    date = models.DateField()
    description = models.CharField(max_length=100, blank=True, null=True)
    def save(self, *args, **kwargs):
        if self.date < timezone.now().date():
            raise ValueError('Holiday date must be in the future or today.')
        super().save(*args, **kwargs)
        Booking = apps.get_model('users', 'Booking')
        # Cancel bookings and reduce booked slots for the holiday
        Booking.objects.filter(slot__date=self.date).update(remarks='Cancelled due to Institute holiday', is_active=False)
        AvailableSlot.objects.filter(date=self.date).update(isAvailable=False)


    #add constraints to prevent overlapping holidays
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['date'], name='unique_holiday')
        ]


class Leave(models.Model):
    counsellor = models.ForeignKey('users.User', on_delete=models.CASCADE, limit_choices_to={'is_ticc_counsellor': True})
    slots = models.ManyToManyField(AvailableSlot, through='LeaveSlot')
    description = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField()
    def save(self, *args, **kwargs):

        #check if start date is in the future or today
        if self.date < timezone.now().date():
            raise ValueError('Start date must be in the future or today')
        super().save(*args, **kwargs)

  
class LeaveSlot(models.Model):
    leave = models.ForeignKey(Leave, on_delete=models.CASCADE)
    slot = models.ForeignKey(AvailableSlot, on_delete=models.CASCADE)