# tasks.py
from celery import shared_task
import time
from django.core.cache import cache

@shared_task(bind=True)
def task_a(self):
    for i in range(5):
        time.sleep(1)
        cache.set(f"task:{self.request.id}:progress", f"{(i+1)*20}%")
    return "done"