# from celery import shared_task
# from safenestapp.worker.tasks import match_missing_child_task  # Adjust import path as needed

# @shared_task
# def match_missing_child_task_celery(report_id):
#     """
#     Celery task wrapper for the core matching logic.
#     """
#     match_missing_child_task(report_id)








from celery import shared_task
from .utils import match_missing_child_photo

@shared_task
def match_missing_child_task(missing_child_id):
    from .models import MissingChild  # Import here to avoid circular import
    try:
        missing_child = MissingChild.objects.get(id=missing_child_id)
        match_missing_child_photo(missing_child)
    except MissingChild.DoesNotExist:
        pass
