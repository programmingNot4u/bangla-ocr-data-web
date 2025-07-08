# api/views.py
import random
import io
import csv
import zipfile
import requests

from django.db.models import Count
from django.http import HttpResponse

from rest_framework import generics, status, views
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from .models import Prompt, Submission
from .serializers import PromptSerializer, SubmissionCreateSerializer, ModeratorSubmissionSerializer
from .services import upload_image_to_cloudinary

class PromptView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        prompts = Prompt.objects.annotate(submission_count=Count('submissions'))
        if not prompts:
            return Response({"error": "No prompts available."}, status=status.HTTP_404_NOT_FOUND)

        weights = [(p.priority / (p.submission_count + 1)) for p in prompts]
        chosen_prompt = random.choices(prompts, weights=weights, k=1)[0]
        serializer = PromptSerializer(chosen_prompt)
        return Response(serializer.data)

class SubmissionCreateView(generics.CreateAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionCreateSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        image_file = serializer.validated_data.pop('image')
        prompt = serializer.validated_data.get('prompt')

        # Upload to Cloudinary
        upload_result = upload_image_to_cloudinary(image_file)
        if not upload_result["success"]:
            return Response({"error": f"Image upload failed: {upload_result['error']}"}, status=status.HTTP_400_BAD_REQUEST)

        # Save submission with Cloudinary URL
        Submission.objects.create(
            prompt=prompt,
            image_url=upload_result["url"],
            public_id=upload_result["public_id"],
        )
        return Response({"message": "Submission successful."}, status=status.HTTP_201_CREATED)

class PendingSubmissionsView(generics.ListAPIView):
    serializer_class = ModeratorSubmissionSerializer
    permission_classes = [IsAdminUser] # Or a custom IsModerator permission

    def get_queryset(self):
        return Submission.objects.filter(status='pending').order_by('submitted_at')

class ReviewSubmissionView(generics.UpdateAPIView):
    queryset = Submission.objects.all()
    serializer_class = ModeratorSubmissionSerializer
    permission_classes = [IsAdminUser] # Or a custom IsModerator permission

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Set the moderator who verified it
        serializer.save(verified_by=request.user)
        return Response(serializer.data)

class DownloadVerifiedSubmissionsView(views.APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        submissions = Submission.objects.filter(status='verified')
        if not submissions.exists():
            return Response({"error": "No verified submissions to download."}, status=status.HTTP_404_NOT_FOUND)

        # Create zip file in memory
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as zip_file:
            # Create CSV
            csv_buffer = io.StringIO()
            writer = csv.writer(csv_buffer)
            writer.writerow(['image_id', 'prompt_text'])

            # Add images and write CSV rows
            for sub in submissions:
                image_id = f"{sub.id}.jpg"
                writer.writerow([image_id, sub.prompt.text])

                try:
                    response = requests.get(sub.image_url, stream=True)
                    if response.status_code == 200:
                         zip_file.writestr(f"images/{image_id}", response.content)
                except requests.exceptions.RequestException:
                    # Skip files that fail to download
                    continue

            # Add CSV to zip
            zip_file.writestr('labels.csv', csv_buffer.getvalue())

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="verified_submissions.zip"'
        return response