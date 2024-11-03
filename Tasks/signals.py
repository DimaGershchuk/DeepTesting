from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task
from .utils import send_notification


@receiver(post_save, sender=Task)
def task_created_handler(sender, instance, created, **kwargs):
    if created:
        send_notification(instance)