from safenestapp.models import MissingChild
from safenestapp.utils import match_found  # Assuming you place the function in `utils.py`


def match_missing_child_task(report_id):
    child = MissingChild.objects.get(id=report_id)
    matched_videos = []
    matched_frames = []
    matched_photos = []

    # Example placeholders for reported videos and photos
    reported_videos = get_reported_videos()  # Replace with actual logic
    reported_photos = get_reported_photos()  # Replace with actual logic

    # Simulate matching process
    for video in reported_videos:
        if match_found(video, child.photo):
            matched_videos.append(video.path)
            matched_frames.append(extract_frame(video))  # Save matched frame path

    for photo in reported_photos:
        if match_found(photo, child.photo):
            matched_photos.append(photo.path)

    # Update child's matched data and status
    child.matched_videos = matched_videos
    child.matched_frames = matched_frames
    child.matched_photos = matched_photos
    child.status = 'Found'
    child.save()

def get_reported_videos():
    """
    Retrieve all reported videos from the FoundChild model.
    """
    from safenestapp.models import FoundChild
    return FoundChild.objects.exclude(video__isnull=True).exclude(video__exact='')


def get_reported_photos():
    """
    Retrieve all reported photos from FoundChild and MatchedChild models.
    """
    from safenestapp.models import FoundChild, MatchedChild

    found_photos = FoundChild.objects.exclude(photo__isnull=True).exclude(photo__exact='')
    matched_photos = MatchedChild.objects.exclude(photo__isnull=True).exclude(photo__exact='')

    return list(found_photos) + list(matched_photos)  # Combine querysets into a single list







#  from safenestapp.models import MissingChild

# def match_missing_child_task(report_id):
#     child = MissingChild.objects.get(id=report_id)
#     matched_videos = []
#     matched_frames = []
#     matched_photos = []

#     # Simulate matching process
#     for video in reported_videos:
#         if match_found(video, child.photo):
#             matched_videos.append(video.path)
#             matched_frames.append(extract_frame(video))  # Save matched frame path

#     for photo in reported_photos:
#         if match_found(photo, child.photo):
#             matched_photos.append(photo.path)

#     # Update the child's matched data and status
#     child.matched_videos = matched_videos
#     child.matched_frames = matched_frames
#     child.matched_photos = matched_photos
#     child.status = 'Found'
#     child.save()