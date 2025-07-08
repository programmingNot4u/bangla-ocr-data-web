# api/urls.py
from django.urls import path
from .views import (
    PromptView,
    SubmissionCreateView,
    PendingSubmissionsView,
    ReviewSubmissionView,
    DownloadVerifiedSubmissionsView,
)

urlpatterns = [
    path('prompt/', PromptView.as_view(), name='get-prompt'),
    path('submissions/', SubmissionCreateView.as_view(), name='create-submission'),
    path('moderator/pending/', PendingSubmissionsView.as_view(), name='pending-submissions'),
    path('moderator/review/<int:pk>/', ReviewSubmissionView.as_view(), name='review-submission'),
    path('download/verified-submissions/', DownloadVerifiedSubmissionsView.as_view(), name='download-verified'),
]