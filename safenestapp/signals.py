from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MissingChild
from .tasks import match_missing_child_task

@receiver(post_save, sender=MissingChild)
def handle_missing_child_report(sender, instance, created, **kwargs):
    if created:
        # Call the Celery task instead of running directly
        match_missing_child_task.delay(instance.id)
