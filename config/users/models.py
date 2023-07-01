from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
import uuid


class UserManager(BaseUserManager):
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address") 

        is_ticc_counsellor = extra_fields.get('is_ticc_counsellor', False)
        
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()

        if not is_ticc_counsellor:
            student, created = Student.objects.get_or_create(user=user)
            if created:
                student.save()

        return user    

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not email:
            raise ValueError("Users must have an email address")   
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()



class User(AbstractUser):
    username=None
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=10)
    full_name = models.CharField(max_length=255)
    is_ticc_counsellor = models.BooleanField(default=False)
    is_ticc_manager = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'phone_number']

    objects = UserManager()

    def __str__(self):
        return self.email


class Student(models.Model):
    gender_choices = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student')
    roll_number = models.CharField(max_length=10, null=True, blank=True, unique=True)
    branch = models.CharField(max_length=5, null=True, blank=True)
    admission_year = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=gender_choices, null=True, blank=True)

    def __str__(self):
        return self.user.email

    def can_book_slot(self, slot):
        return slot not in self.appointments.all() and slot.slots_booked < slot.capacity


class Booking(models.Model):
    REMARK_CHOICES = (
        ('Pending', 'Pending'),
        ('Cancelled by student', 'Cancelled by student'),
        ('Cancelled by counsellor', 'Cancelled by counsellor'),
        ('Completed', 'Completed'),
        ('Missed by student', 'Missed by student'),
        ('Cancelled due to Institute holiday', 'Cancelled due to Institute holiday'),
        ('Counsellor on leave', 'Counsellor on leave')
    )
    slot = models.ForeignKey('slots.AvailableSlot', on_delete=models.CASCADE, limit_choices_to={'isAvailable': True})
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='bookings')
    additional_info = models.TextField(null=True, blank=True)
    assigned_counsellor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_ticc_counsellor': True}, null=True, blank=True)
    remarks = models.CharField(max_length=40, choices=REMARK_CHOICES, default='Pending')
    is_active = models.BooleanField(default=True)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student', 'slot'], 
                                    name='unique_booking',
                                    condition=Q(remarks__in=['Pending', 'Completed', 'Missed by student']))
        ]

    def save(self, *args, **kwargs):
        if self._state.adding:  # Check if it's a new booking
            # Check if the slot is available before saving the booking
            if not self.slot.isAvailable:
                raise ValidationError("The selected slot is not available for booking.")
            # Increment the number of slots booked
            self.slot.slots_booked += 1
            if self.slot.slots_booked == self.slot.capacity:
                self.slot.isAvailable = False
            self.slot.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.user.email} - {self.slot}"
    
