from django.db import models
from django.contrib.auth.models import User

class MissingChild(models.Model):
    STATUS_CHOICES = [
        ('Missing', 'Missing'),
        ('Matched', 'Matched'),
    ]
    
    parent = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the parent who submitted the report
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    last_seen_location = models.CharField(max_length=255)
    last_seen_date = models.DateField()
    contact_details = models.TextField()
    photo = models.ImageField(upload_to='missing_children_photos/')
    additional_info = models.TextField(blank=True, null=True)
    date_reported = models.DateTimeField(auto_now_add=True)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Missing')  # Add status field here

    def __str__(self):
        return f"{self.name} - {self.status} - Reported by {self.parent.username}"

# Found Child Report Model
class FoundChild(models.Model):
    reporter_name = models.CharField(max_length=100)
    description = models.TextField()
    found_location = models.CharField(max_length=255)
    found_date = models.DateField()
    contact_details = models.TextField()
    date_reported = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, null=True, blank=True)  # Allow null
    photo = models.ImageField(upload_to='found_children_photos/')
    video = models.FileField(upload_to='found_children_videos/', null=True, blank=True)

    def __str__(self):
        return f"Found Child Reported by {self.reporter_name}"

class MatchedChild(models.Model):
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='matched_children_photos/')
    matched_at = models.DateTimeField(auto_now_add=True)

# Statistics Model (Optional)
class Statistics(models.Model):
    date = models.DateField(auto_now_add=True)
    children_found = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.children_found} children found on {self.date}"
