# complaints/serializers.py
from rest_framework import serializers
from .models import Complaint, WebsiteFeedback

class ComplaintSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Complaint
        fields = [
            'id', 'user', 'type', 'district', 'place', 'location', 'issue',
            'description', 'phone', 'photo', 'status',
            'submitted_at',           # FIXED: was 'created_at'
            'accepted_at', 'resolved_at',
            'resolution_notes', 'resolution_image'
        ]

class WebsiteFeedbackSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = WebsiteFeedback
        fields = ['id', 'user', 'feedback', 'created_at']  # This one is OK