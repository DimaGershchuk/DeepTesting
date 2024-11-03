import requests
from django.db import transaction
from .models import Task


def fetch_tasks_from_api(api_url):
    response = requests.get(api_url)
    tasks_data = response.json()
    return tasks_data


def is_task_completed(status):
    return status == "completed"


def send_notification(task):
    print(f"Notification sent for:  {task.title}")


def create_tasks_bulk(tasks_data):
    try:
        with transaction.atomic():
            for task_data in tasks_data:
                Task.objects.create(**task_data)
    except Exception as e:
        print(f"Error occurred: {e}")
        raise
