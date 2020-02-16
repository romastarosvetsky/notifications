from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from envs import env

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notifications.settings')

REDIS_HOST = env('REDIS_HOST', default='127.0.0.1')
REDIS_PORT = env('REDIS_PORT', default='6379')

app = Celery('notifications', broker=f'redis://{REDIS_HOST}:{REDIS_PORT}/0')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
