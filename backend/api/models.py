# api/models.py
from django.db import models
from django.contrib.auth.models import User

class Prompt(models.Model):
    text = models.TextField(help_text="Prompt content (Bangla)")
    priority = models.IntegerField(default=1, help_text="Integer for weighted randomness")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:50]

class Submission(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('unverified', 'Unverified'),
    ]

    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE, related_name='submissions')
    image_url = models.URLField(max_length=500, help_text="URL of the uploaded image from Cloudinary")
    public_id = models.CharField(max_length=200, help_text="Cloudinary public ID for the image")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True, help_text="Notes from moderator")
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission for '{self.prompt.text[:20]}...' on {self.submitted_at.strftime('%Y-%m-%d')}"