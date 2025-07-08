# api/serializers.py
from rest_framework import serializers
from .models import Prompt, Submission

class PromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prompt
        fields = ['id', 'text']

class SubmissionCreateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True, required=True)

    class Meta:
        model = Submission
        fields = ['prompt', 'image']

class ModeratorSubmissionSerializer(serializers.ModelSerializer):
    prompt_text = serializers.CharField(source='prompt.text', read_only=True)
    submitted_by = serializers.CharField(source='verified_by.username', read_only=True, default='Anonymous')

    class Meta:
        model = Submission
        fields = ['id', 'prompt_text', 'image_url', 'status', 'notes', 'submitted_by', 'submitted_at']
        read_only_fields = ['id', 'prompt_text', 'image_url', 'submitted_by', 'submitted_at']