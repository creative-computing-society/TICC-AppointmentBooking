from __future__ import absolute_import, unicode_literals
from celery import Celery
from django.conf import settings
import os
from celery.schedules import crontab


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.conf.enable_utc = False
app.conf.update(timezone='Asia/Kolkata')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Set the Celery beat scheduler to operate in the 'Asia/Kolkata' time zone
app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'

# Add the schedule for the generate_slots task
app.conf.beat_schedule = {
    'generate_slots': {
        'task': 'slots.tasks.generate_slots',
        'schedule': crontab(hour=0, minute=5),  # Run at 12:05 A.M. every day
    },
    'send_6AM_reminders': {
        'task': 'users.tasks.send_6AM_booking_notification',
        'schedule': crontab(hour=6, minute=0),  # Run at 6:00 A.M. every day  
    }, 
    'send_1hr_reminders': {
        'task': 'users.tasks.send_notification_1hrbefore_booking',
        'schedule': crontab(hour='8-15', minute='0,30'),
    },
    'disable_slots': {
        'task': 'slots.tasks.disable_slots_after_they_are_over',
        'schedule': crontab(hour='9-17', minute='0,30'),
    },
}