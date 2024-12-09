

# from celery import shared_task
# from .utils import match_missing_child_photo

# @shared_task
# def match_missing_child_task(missing_child_id):
#     from .models import MissingChild  # Import here to avoid circular import
#     try:
#         missing_child = MissingChild.objects.get(id=missing_child_id)
#         match_missing_child_photo(missing_child)
#     except MissingChild.DoesNotExist:
#         pass


from celery import shared_task
from .utils import match_missing_child_photo


@shared_task
def match_missing_child_task(missing_child_id):
    from .models import MissingChild  # Import here to avoid circular imports
    try:
        missing_child = MissingChild.objects.get(id=missing_child_id)
        match_missing_child_photo(missing_child)
    except MissingChild.DoesNotExist:
        print(f"MissingChild with ID {missing_child_id} does not exist.")
