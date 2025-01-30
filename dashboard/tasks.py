# myapp/tasks.py
from celery import shared_task
import time

@shared_task
def my_periodic_task():
    print("Running my periodic task")
    # Your function logic here
    time.sleep(2)  # Simulating work that takes some time
    return "Task complete"
