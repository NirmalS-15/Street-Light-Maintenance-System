# complaints/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# === CHOICES ===
TYPE_CHOICES = [
    ('Normal', 'Normal'),
    ('Urgent', 'Urgent'),
]

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('resolved', 'Resolved'),
]


# === COMPLAINT MODEL (ONLY ONCE) ===
class Complaint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='Normal')
    district = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    issue = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    photo = models.ImageField(upload_to='complaints/', blank=True, null=True)

    # STATUS & TIMESTAMPS
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(default=timezone.now)
    accepted_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    resolution_image = models.ImageField(upload_to='resolutions/', blank=True, null=True)

    # RATING & FEEDBACK
    user_rating = models.PositiveSmallIntegerField(
        choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)],
        null=True, blank=True
    )
    user_review = models.TextField(blank=True, null=True)
    rated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.issue} - {self.place}"


# === WEBSITE FEEDBACK ===
class WebsiteFeedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Feedback by {self.user.username}"


# === COMPLAINT REPLY ===
class ComplaintReply(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='replies')
    message = models.TextField()
    photo = models.ImageField(upload_to='replies/', blank=True, null=True)
    sent_by_admin = models.BooleanField(default=True)  # True = KSEB, False = User
    viewed_by_admin = models.BooleanField(default=False)  # Track if admin has viewed user replies
    sent_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Reply to #{self.complaint.id}"
