from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from .models import Booking
from django.utils.html import strip_tags
from django.conf import settings
import os
import datetime

@shared_task
def send_6AM_booking_notification():
    # Get the current date
    current_date = timezone.now().date()

    # Retrieve all bookings for the current date
    bookings = Booking.objects.filter(slot__date=current_date)
    # bookings = Booking.objects.all() #for testing
    print('found ' + str(len(bookings)) + ' bookings')
    # Send email notifications to users with bookings
    for booking in bookings:
        reciever_email = booking.student.user.email
        subject = 'Please Confirm Your Availability for Your TICC Appointment'
        cancellation_link = os.environ.get('CANCELLATION_EMAIL_BASE_URL') + 'api/bookings/emailcancellation/' + str(booking.token) + '/'

         # Modify the date and time format in the context dictionary
        slot_date = booking.slot.date.strftime('%A, %B %d')
        slot_start_time = booking.slot.start_time.strftime('%I:%M %p')
        context = {
            'student_name': booking.student.user.full_name,
            'slot_date': slot_date,
            'slot_start_time': slot_start_time,
            'cancel_booking_link': cancellation_link,
        }
        html_message = render_to_string('users/6AMConfirmation.html', context)
        message = strip_tags(html_message)
        send_mail(subject, message, settings.EMAIL_HOST_USER  , [reciever_email], html_message=html_message, fail_silently=False)
        print('sent email to ' + reciever_email)


@shared_task
def send_notification_1hrbefore_booking():
    # Get the current date and time
    current_datetime = timezone.now()

    # Calculate the target time for sending the notification (1 hour before each booking)
    target_datetime = current_datetime - datetime.timedelta(hours=1)

    # Retrieve the bookings for the target time
    bookings = Booking.objects.filter(slot__date=current_datetime.date(), slot__start_time=target_datetime.time())
    print('found ' + str(len(bookings)) + ' bookings')

    # Send email notifications to users with bookings
    for booking in bookings:
        receiver_email = booking.student.user.email
        subject = 'Reminder: Your TICC Appointment is in 1 hour'
        cancellation_link = os.environ.get('BASE_URL') + 'api/bookings/emailcancellation/' + str(booking.token) + '/'

        # Modify the date and time format in the context dictionary
        slot_date = booking.slot.date.strftime('%A, %B %d')
        slot_start_time = booking.slot.start_time.strftime('%I:%M %p')
        context = {
            'student_name': booking.student.user.full_name,
            'slot_date': slot_date,
            'slot_start_time': slot_start_time,
            'cancel_booking_link': cancellation_link,
        }
        html_message = render_to_string('users/booking_notification.html', context)
        message = strip_tags(html_message)
        send_mail(subject, message, settings.EMAIL_HOST_USER, [receiver_email], html_message=html_message, fail_silently=False)
        print('sent email to ' + receiver_email)


@shared_task
def send_booking_confirmation_email(reciever_email, context):
    subject = 'Your TICC Appointment Has Been Booked'

    # Modify the date and time format in the context dictionary
    
    html_message = render_to_string('users/bookingconfirmation.html', context)
    message = strip_tags(html_message)
    send_mail(subject, message, settings.EMAIL_HOST_USER, [reciever_email], html_message=html_message, fail_silently=False)
    print('sent email to ' + reciever_email)