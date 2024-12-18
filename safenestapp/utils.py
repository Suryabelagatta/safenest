import face_recognition
import os
import cv2
from django.conf import settings
from .models import MissingChild
import numpy as np

# Utility function to load face encodings from images
def load_encodings_from_folder(folder_path):
    print('Loading encodings from folder...')
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


# Process a video file to extract face encodings and find the best matching frame
def process_video(video_path, missing_encoding):
    print('Processing video for best matched frame...')
    matched_frame = None
    highest_similarity = 0
    best_frame_number = None

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
            face_distances = face_recognition.face_distance([missing_encoding], encoding)
            similarity = round((1 - face_distances[0]) * 100, 2)

            if similarity > highest_similarity:
                highest_similarity = similarity
                matched_frame = frame.copy()
                best_frame_number = frame_count

        frame_count += 1

    video_capture.release()

    return matched_frame, highest_similarity, best_frame_number


def match_missing_child_photo(missing_child):
    print(f"Matching missing child photo: {missing_child.photo.path}")

    # Load encodings from reported photos
    reported_photo_encodings = load_encodings_from_folder(
        os.path.join(settings.MEDIA_ROOT, 'found_children_photos')
    )

    # Load the new missing child photo
    new_image = face_recognition.load_image_file(missing_child.photo.path)
    new_encoding = face_recognition.face_encodings(new_image)

    if not new_encoding:
        print("No face found in the uploaded image.")
        return

    new_encoding = new_encoding[0]

    # Find the top 3 matching photos
    photo_distances = []
    for known_encoding, file_name in reported_photo_encodings:
        face_distances = face_recognition.face_distance([known_encoding], new_encoding)
        similarity = round((1 - face_distances[0]) * 100, 2)
        photo_distances.append((similarity, file_name))

    # Sort to get top 3 photos with highest similarity
    photo_distances.sort(reverse=True, key=lambda x: x[0])
    matched_photos = [photo for _, photo in photo_distances[:3]]  # Top 3 matches

    # Load and process the videos to find the best matching frame
    matched_frames = []
    matched_videos = []
    video_folder = os.path.join(settings.MEDIA_ROOT, 'found_children_videos')
    if os.path.exists(video_folder):
        for video_file in os.listdir(video_folder):
            video_path = os.path.join(video_folder, video_file)
            if video_file.lower().endswith(('.mp4', '.avi', '.mkv')):
                matched_frame, similarity, frame_number = process_video(video_path, new_encoding)
                if matched_frame is not None:
                    matched_videos.append(video_file)
                    matched_frames.append(f"Frame-{frame_number} - Similarity: {similarity}%")

    # Update the MissingChild model
    if matched_photos or matched_videos:
        print(f"Match found for {missing_child.name}. Updating status to 'Found'.")

        # Update fields explicitly
        missing_child.status = 'Found'
        missing_child.matched_photos = matched_photos
        missing_child.matched_videos = matched_videos
        missing_child.matched_frames = matched_frames

        # Save the updated instance to the database
        missing_child.save(update_fields=["status", "matched_photos", "matched_videos", "matched_frames"])

        # Send notification email (optional)
        #missing_child.send_status_update_email()
    else:
        print("No match found for the uploaded photo.")
