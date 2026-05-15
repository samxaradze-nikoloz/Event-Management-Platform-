import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-event-reminders': {
        'task': 'notifications.tasks.send_event_reminders',
        'schedule': crontab(hour=9, minute=0),
    },
}