from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_phone.settings')

app = Celery('Project')
app.conf.enable_utc = False
app.conf.update(timezone='Asia/Dhaka')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

# app.conf.beat_schedule = {
#     'unlock_accounts': {
#         'task': 'phone.tasks.unlock_accounts',
#         'schedule': crontab(minute='*/1'),
#     },
# }
