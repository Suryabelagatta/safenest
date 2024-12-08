from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from .models import MissingChild, FoundChild, Statistics
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import logout
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from .utils import match_missing_child_background, match_found_child
import os
from django.http import JsonResponse
import threading
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import MissingChildForm
from django.conf import settings

@login_required
def delete_report(request, report_id):
    child = get_object_or_404(MissingChild, id=report_id, parent=request.user)
    if request.method == 'POST':
        child.delete()
        return HttpResponseRedirect(reverse('parent_dashboard'))
    return render(request, 'confirm_delete.html', {'child': child})

@login_required
def edit_report(request, report_id):
    child = get_object_or_404(MissingChild, id=report_id, parent=request.user)
    if request.method == 'POST':
        form = MissingChildForm(request.POST, request.FILES, instance=child)
        if form.is_valid():
            form.save()
            # Optional: Send email notification if status is updated
            if 'status' in form.changed_data:
                child.send_status_update_email()
            return HttpResponseRedirect(reverse('parent_dashboard'))
    else:
        form = MissingChildForm(instance=child)
    return render(request, 'edit_report.html', {'form': form, 'child': child})

@login_required
def view_report(request, report_id):
    child = get_object_or_404(MissingChild, id=report_id, parent=request.user)
    matched_videos = [os.path.join(settings.MEDIA_URL, path) for path in child.matched_videos]
    matched_frames = [os.path.join(settings.MEDIA_URL, path) for path in child.matched_frames]
    matched_photos = [os.path.join(settings.MEDIA_URL, path) for path in child.matched_photos]

    return render(request, 'view_report.html', {
        'child': child,
        'matched_videos': matched_videos,
        'matched_frames': matched_frames,
        'matched_photos': matched_photos,
    })

# View for uploading found child photo/video
def upload_found_child(request):
    if request.method == 'POST' and 'photo' in request.FILES:
        uploaded_file = request.FILES['photo']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_url = fs.url(filename)

        found_child = FoundChild.objects.create(name=request.POST.get('name'), photo=uploaded_file)

        # Match the found child
        match_found_child(found_child)

        return render(request, 'upload.html', {
            'uploaded_file_url': file_url,
            'message': "Found child photo uploaded and matched if any."
        })
    elif request.method == 'POST' and 'video' in request.FILES:
        uploaded_video = request.FILES['video']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_video.name, uploaded_video)
        file_url = fs.url(filename)

        found_child = FoundChild.objects.create(name=request.POST.get('name'), video=uploaded_video)

        # Match the found child
        match_found_child(found_child)

        return render(request, 'upload.html', {
            'uploaded_file_url': file_url,
            'message': "Found child video uploaded and matched if any."
        })

    return render(request, 'upload.html')

def custom_logout(request):
    logout(request)
    return redirect('login')  # Redirect to the login page or homepage


class CustomLoginView(LoginView):
    template_name = 'login.html'

    def get_success_url(self):
        return '/parent_dashboard/' 

from .tasks import match_missing_child_task

@login_required
def report_missing(request):
    if request.method == 'POST':
        # Collect data and create the missing child report
        missing_child = MissingChild.objects.create(
            parent=request.user,
            name=request.POST['name'],
            age=request.POST['age'],
            gender=request.POST['gender'],
            last_seen_location=request.POST['last_seen_location'],
            last_seen_date=request.POST['last_seen_date'],
            contact_details=request.POST['contact_details'],
            photo=request.FILES['photo'],
        )
        # Trigger background processing via Celery
        #match_missing_child_task.delay(missing_child.id)

        messages.success(request, "Report submitted! We are working on it.")
        return redirect('parent_dashboard')

    return render(request, 'report_missing.html')

@login_required
def parent_dashboard(request):
    missing_children = MissingChild.objects.filter(parent=request.user).order_by('-date_reported')
    #print(missing_children)
    return render(request, 'parent_dashboard.html', {'missing_children': missing_children})


def report_found(request):
    if request.method == 'POST':
        reporter_name = request.POST['reporter_name']
        description = request.POST['description']
        found_location = request.POST['found_location']
        found_date = request.POST['found_date']
        contact_details = request.POST['contact_details']
        photo = request.FILES['photo']
        video = request.FILES['video']

        FoundChild.objects.create(
            reporter_name=reporter_name,
            description=description,
            found_location=found_location,
            found_date=found_date,
            contact_details=contact_details,
            photo=photo,
            video=video,
        )
        messages.success(request, "Found child report submitted successfully.")
        return redirect('dashboard')
    return render(request, 'report_found.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            login(request, user)  # Automatically log in after registration
            return redirect('parent_dashboard')
    return render(request, 'register.html')


from .models import MissingChild, FoundChild, Statistics

def dashboard(request):
    children_found_count = Statistics.objects.aggregate_count() if Statistics.objects.exists() else 0
    cases_solved_count = FoundChild.objects.count()
    active_reports_count = MissingChild.objects.count()

    context = {
        'children_found': children_found_count,
        'cases_solved': cases_solved_count,
        'active_reports': active_reports_count,
    }
    return render(request, 'dashboard.html', context)


