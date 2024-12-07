import face_recognition
import os
import shutil
import cv2
from django.conf import settings
from .models import MissingChild, FoundChild
import threading

# Function to run in background
def match_missing_child_background(missing_child):
    match_missing_child_photo(missing_child)

# Update the report_missing view to start the process in a background thread
def report_missing(request):
    if request.method == 'POST':
        name = request.POST['name']
        age = request.POST['age']
        gender = request.POST['gender']
        last_seen_location = request.POST['last_seen_location']
        last_seen_date = request.POST['last_seen_date']
        contact_details = request.POST['contact_details']
        photo = request.FILES['photo']

        # Create the missing child report
        missing_child = MissingChild.objects.create(
            parent=request.user,
            name=name,
            age=age,
            gender=gender,
            last_seen_location=last_seen_location,
            last_seen_date=last_seen_date,
            contact_details=contact_details,
            photo=photo,
        )
        
        # Run the photo matching in the background
        threading.Thread(target=match_missing_child_background, args=(missing_child,)).start()

        # Notify the user
        messages.success(request, "Missing child report submitted successfully. We are looking for matches.")
        return redirect('parent_dashboard')

    return render(request, 'report_missing.html')

# Utility function to load face encodings from images
def load_encodings_from_folder(folder_path):
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
    encodings = []
    video_capture = cv2.VideoCapture(video_path)

    while video_capture.isOpened():
        ret, frame = video_capture.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame, model="cnn")
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for encoding in face_encodings:
            encodings.append(encoding)

    video_capture.release()
    return encodings

# Match missing child photo
def match_missing_child_photo(missing_child):
    print(f"Matching missing child photo: {missing_child.photo.path}")

    # Load encodings from reported photos
    reported_photo_encodings = load_encodings_from_folder(
        os.path.join(settings.MEDIA_ROOT, 'found_children_photos')
    )

    # Load encodings from reported videos
    reported_video_encodings = []
    video_folder = os.path.join(settings.MEDIA_ROOT, 'found_children_videos')
    if os.path.exists(video_folder):
        for video_file in os.listdir(video_folder):
            video_path = os.path.join(video_folder, video_file)
            if video_file.lower().endswith(('.mp4', '.avi', '.mkv')):
                reported_video_encodings.extend(process_video(video_path))

    # Load the new missing child photo
    new_image = face_recognition.load_image_file(missing_child.photo.path)
    new_encoding = face_recognition.face_encodings(new_image)

    if not new_encoding:
        print("No face found in the uploaded image.")
        return

    new_encoding = new_encoding[0]

    # Check for matches
    match_found = False
    for known_encoding, file_name in reported_photo_encodings:
        if face_recognition.compare_faces([known_encoding], new_encoding)[0]:
            match_found = True
            print(f"Match found with reported photo: {file_name}")
            break

    for encoding in reported_video_encodings:
        if face_recognition.compare_faces([encoding], new_encoding)[0]:
            match_found = True
            print("Match found in reported video.")
            break

    # Update status or move the photo to matched folder
    if match_found:
        print(f"Match found for {missing_child.name}. Updating status to 'Matched'.")
        missing_child.status = 'Matched'
        missing_child.save()
        # Notify parent (additional implementation can be added here)
    else:
        print("No match found. Moving photo to matched folder.")
        matched_folder = os.path.join(settings.MEDIA_ROOT, 'matched_children_photos')
        if not os.path.exists(matched_folder):
            os.makedirs(matched_folder)
        shutil.move(
            missing_child.photo.path,
            os.path.join(matched_folder, os.path.basename(missing_child.photo.path))
        )

# Match found child photo/video with matched children
def match_found_child(found_child):
    print(f"Matching found child: {found_child.photo.path}")

    # Load encodings from matched photos
    matched_encodings = load_encodings_from_folder(
        os.path.join(settings.MEDIA_ROOT, 'matched_children_photos')
    )

    # Process the new file (photo or video)
    if found_child.photo:
        new_image = face_recognition.load_image_file(found_child.photo.path)
        new_encoding = face_recognition.face_encodings(new_image)
        if not new_encoding:
            print("No face found in the uploaded image.")
            return
        new_encodings = [new_encoding[0]]
    elif hasattr(found_child, 'video') and found_child.video:
        new_encodings = process_video(found_child.video.path)
    else:
        print("No photo or video found.")
        return

    # Check for matches
    for new_encoding in new_encodings:
        for known_encoding, file_name in matched_encodings:
            if face_recognition.compare_faces([known_encoding], new_encoding)[0]:
                print(f"Match found with matched photo: {file_name}")
                # Logic for handling the match can be implemented (e.g., notify parent or authorities)
                break
