import face_recognition
import os
import cv2
from django.conf import settings
from .models import MissingChild
import concurrent.futures 

# Utility function to load face encodings from images
def load_encodings_from_folder(folder_path):
    print('load function')
    encodings = []
    if os.path.exists(folder_path):
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if file_name.lower().endswith(('.jpg', '.jpeg', '.png')) and os.path.isfile(file_path):
                image = face_recognition.load_image_file(file_path)
                encoding = face_recognition.face_encodings(image)
                if encoding:
                    encodings.append((encoding[0], file_name))
    return encodings


# Process a video file to extract face encodings
def process_video(video_path):
    print('processing video function')
    encodings = []
    matched_frames = []
    video_capture = cv2.VideoCapture(video_path)
    frame_count = 0

    while video_capture.isOpened():
        ret, frame = video_capture.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame, model="cnn")
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for encoding in face_encodings:
            encodings.append(encoding)
            matched_frames.append(f"Frame-{frame_count}.jpg")  # Mocked frame reference

        frame_count += 1

    video_capture.release()
    return encodings, matched_frames

def match_missing_child_photo(missing_child):
    print(f"Matching missing child photo: {missing_child.photo.path}")

    # Load encodings from reported photos
    reported_photo_encodings = load_encodings_from_folder(
        os.path.join(settings.MEDIA_ROOT, 'found_children_photos')
    )

    # Load encodings from reported videos
    reported_video_encodings = []
    matched_frames = []
    video_folder = os.path.join(settings.MEDIA_ROOT, 'found_children_videos')
    if os.path.exists(video_folder):
        for video_file in os.listdir(video_folder):
            video_path = os.path.join(video_folder, video_file)
            if video_file.lower().endswith(('.mp4', '.avi', '.mkv')):
                video_encodings, frames = process_video(video_path)
                reported_video_encodings.extend(video_encodings)
                matched_frames.extend(frames)

    # Load the new missing child photo
    new_image = face_recognition.load_image_file(missing_child.photo.path)
    new_encoding = face_recognition.face_encodings(new_image)

    if not new_encoding:
        print("No face found in the uploaded image.")
        return

    new_encoding = new_encoding[0]

    # Check for matches
    matched_photos = []
    matched_videos = []
    for known_encoding, file_name in reported_photo_encodings:
        if face_recognition.compare_faces([known_encoding], new_encoding)[0]:
            matched_photos.append(file_name)

    for encoding in reported_video_encodings:
        if face_recognition.compare_faces([encoding], new_encoding)[0]:
            matched_videos.append(video_folder)  # Append video references

    # Update the MissingChild model
    if matched_photos or matched_videos:
        print(f"Match found for {missing_child.name}. Updating status to 'Found'.")

        # Update fields explicitly
        missing_child.status = 'Found'
        missing_child.matched_photos = missing_child.matched_photos + matched_photos
        missing_child.matched_videos = missing_child.matched_videos + matched_videos
        missing_child.matched_frames = missing_child.matched_frames + matched_frames

        # Save the updated instance to the database
        missing_child.save(update_fields=["status", "matched_photos", "matched_videos", "matched_frames"])

        # Send notification email
        #missing_child.send_status_update_email()
    else:
        print("No match found for the uploaded photo.")



# def match_missing_child_photo(missing_child):
#     print(f"Matching missing child photo: {missing_child.photo.path}")

#     # Load encodings from reported photos
#     reported_photo_encodings = load_encodings_from_folder(
#         os.path.join(settings.MEDIA_ROOT, 'found_children_photos')
#     )
#     print('loading encodings')
#     # Load encodings from reported videos with parallel processing
#     video_folder = os.path.join(settings.MEDIA_ROOT, 'found_children_videos')
#     reported_video_encodings = []
#     matched_frames = []

#     if os.path.exists(video_folder):
#         video_paths = [os.path.join(video_folder, video_file) for video_file in os.listdir(video_folder)
#                        if video_file.lower().endswith(('.mp4', '.avi', '.mkv'))]
        
#         print('using concurent processing')
#         # Use concurrent processing to handle multiple video files in parallel
#         with concurrent.futures.ThreadPoolExecutor() as executor:
#             futures = [executor.submit(process_video, video_path) for video_path in video_paths]
#             for future in concurrent.futures.as_completed(futures):
#                 video_encodings, frames = future.result()
#                 reported_video_encodings.extend(video_encodings)
#                 matched_frames.extend(frames)

#     # Load the new missing child photo and extract face encodings
#     try:
#         new_image = face_recognition.load_image_file(missing_child.photo.path)
#         new_encodings = face_recognition.face_encodings(new_image)
#     except Exception as e:
#         print(f"Error loading or processing photo: {e}")
#         return

#     if not new_encodings:
#         print("No face found in the uploaded image.")
#         return

#     new_encoding = new_encodings[0]

#     # Check for matches
#     matched_photos = []
#     matched_videos = []
#     best_frames = []

#     # Match against reported photos
#     for known_encoding, file_name in reported_photo_encodings:
#         if face_recognition.compare_faces([known_encoding], new_encoding)[0]:
#             matched_photos.append(file_name)

#     # Match against reported video encodings and capture frames
#     for encoding, frame, video_path in zip(reported_video_encodings, matched_frames, video_paths):
#         if face_recognition.compare_faces([encoding], new_encoding)[0]:
#             matched_videos.append(video_path)  # Store video reference (you can customize this)
#             best_frames.append(frame)

#     # Limit to top 3 photos, top 2 videos, and 1 frame per video
#     matched_photos = matched_photos[:3]
#     matched_videos = matched_videos[:2]
#     best_frames = best_frames[:2]  # Assuming 1 best frame per video

#     # Return the matched photos and videos (no database update or frame conversion)
#     print("Matched Photos:", matched_photos)
#     print("Matched Videos:", matched_videos)
#     print("Matched Frames:", best_frames)
    
#     return matched_photos, matched_videos, best_frames  # Return matched results


