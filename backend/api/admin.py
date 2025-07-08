# api/admin.py

import io
import csv
import zipfile
import requests
from django.contrib import admin, messages
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Prompt, Submission

@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = ('text', 'priority', 'submission_count', 'created_at')
    search_fields = ('text',)
    list_filter = ('priority',)
    ordering = ('-priority', '-created_at')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(submission_count=Count('submissions'))
        return queryset

    def submission_count(self, obj):
        return obj.submission_count
    submission_count.admin_order_field = 'submission_count'
    submission_count.short_description = 'Submissions'


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'prompt', 'image_preview', 'status', 'submitted_at', 'verified_by')
    list_filter = ('status', 'prompt', 'verified_by', 'submitted_at')
    search_fields = ('prompt__text', 'id')
    ordering = ('-submitted_at',)
    readonly_fields = ('image_preview', 'prompt', 'public_id', 'submitted_at', 'verified_by')
    
    actions = ['mark_verified', 'mark_unverified']

    fieldsets = (
        ('Submission Details', {'fields': ('prompt', 'status', 'submitted_at')}),
        ('Image', {'fields': ('image_preview', 'image_url', 'public_id')}),
        ('Moderation', {'fields': ('notes', 'verified_by')}),
    )
    
    def image_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-height: 100px; max-width: 150px;" /></a>',
                obj.image_url, obj.image_url
            )
        return "No Image"
    image_preview.short_description = 'Handwriting Sample'

    def mark_verified(self, request, queryset):
        updated_count = queryset.update(status='verified', verified_by=request.user)
        self.message_user(request, f'{updated_count} submissions were successfully marked as verified.')
    mark_verified.short_description = "Mark selected submissions as Verified"

    def mark_unverified(self, request, queryset):
        updated_count = queryset.update(status='unverified', verified_by=request.user)
        self.message_user(request, f'{updated_count} submissions were successfully marked as unverified.')
    mark_unverified.short_description = "Mark selected submissions as Unverified"

    # --- Custom Download Functionality (Template-Free) ---
    
    def get_urls(self):
        """Adds a custom URL for the download view."""
        urls = super().get_urls()
        custom_urls = [
            path(
                'download-verified/',
                self.admin_site.admin_view(self.download_verified_view),
                name='api_submission_download_verified' # Use a unique name
            )
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        """Override to add a custom message with the download link."""
        # The URL for our custom view
        download_url = reverse('admin:api_submission_download_verified')
        
        # Add the message with a safe-to-render HTML link
        messages.add_message(
            request,
            messages.INFO,
            mark_safe(f'<a href="{download_url}" class="button">Download All Verified Submissions</a>')
        )
        
        # Continue with the default changelist view
        return super().changelist_view(request, extra_context)

    def download_verified_view(self, request):
        """Handles the logic for creating and serving the zip file."""
        submissions = Submission.objects.filter(status='verified')
        if not submissions.exists():
            self.message_user(request, "There are no verified submissions to download.", level='warning')
            return HttpResponseRedirect("../")

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as zip_file:
            csv_buffer = io.StringIO()
            writer = csv.writer(csv_buffer)
            writer.writerow(['image_id', 'prompt_text'])

            for sub in submissions:
                image_id = f"{sub.id}.jpg"
                writer.writerow([image_id, sub.prompt.text])
                
                try:
                    response = requests.get(sub.image_url, stream=True)
                    if response.status_code == 200:
                        zip_file.writestr(f"images/{image_id}", response.content)
                except requests.exceptions.RequestException:
                    continue

            zip_file.writestr('labels.csv', csv_buffer.getvalue())

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="verified_submissions.zip"'
        return response