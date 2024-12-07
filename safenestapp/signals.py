from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MissingChild
from .utils import match_missing_child_photo

@receiver(post_save, sender=MissingChild)
def handle_missing_child_report(sender, instance, created, **kwargs):
    if created:
        match_missing_child_photo(instance)
