# complaints/views.py

from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from .models import WebsiteFeedback
from django.utils import timezone
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Complaint, WebsiteFeedback, ComplaintReply
from .serializers import ComplaintSerializer, WebsiteFeedbackSerializer
from .forms import ComplaintReplyForm


# ====================== API VIEWSETS ======================
class ComplaintViewSet(viewsets.ModelViewSet):
    serializer_class = ComplaintSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        if self.request.user.groups.filter(name='KSEB').exists() or self.request.user.is_staff:
            return Complaint.objects.all()
        return Complaint.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("You must be logged in to submit a complaint.")
        complaint = serializer.save(user=self.request.user)
        send_mail(
            'Complaint Received',
            f'Your {complaint.type} complaint ({complaint.issue}) has been received.',
            'priyaslms@gmail.com',
            [complaint.user.email],
            fail_silently=True
        )

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        if not (request.user.groups.filter(name='KSEB').exists() or request.user.is_staff):
            return Response({'error': 'Permission denied'}, status=403)

        complaint = self.get_object()
        complaint.status = 'accepted'
        complaint.accepted_at = timezone.now()
        complaint.save()

        send_mail(
            'Complaint Accepted',
            f'Your complaint ({complaint.issue}) has been accepted on {complaint.accepted_at}.',
            'priyaslms@gmail.com',
            [complaint.user.email],
            fail_silently=True
        )

        if 'text/html' in request.META.get('HTTP_ACCEPT', '') or request.content_type == 'application/x-www-form-urlencoded':
            messages.success(request, f"Complaint #{complaint.id} accepted!")
            return redirect('complaints:kseb_dashboard')

        return Response({'status': 'complaint accepted'})

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def resolve(self, request, pk=None):
        if not (request.user.groups.filter(name='KSEB').exists() or request.user.is_staff):
            return Response({'error': 'Permission denied'}, status=403)

        complaint = self.get_object()
        complaint.status = 'resolved'
        complaint.resolved_at = timezone.now()
        complaint.resolution_notes = request.data.get('resolution_notes', '')
        if 'resolution_image' in request.FILES:
            complaint.resolution_image = request.FILES['resolution_image']
        complaint.save()

        image_url = request.build_absolute_uri(complaint.resolution_image.url) if complaint.resolution_image else "No image"
        send_mail(
            'Complaint Resolved',
            f'Your complaint ({complaint.issue}) was resolved on {complaint.resolved_at}.\n\n'
            f'Resolution Notes: {complaint.resolution_notes}\n'
            f'View image: {image_url}',
            'priyaslms@gmail.com',
            [complaint.user.email],
            fail_silently=True
        )

        if 'text/html' in request.META.get('HTTP_ACCEPT', '') or request.content_type == 'application/x-www-form-urlencoded':
            messages.success(request, f"Complaint #{complaint.id} resolved!")
            return redirect('complaints:kseb_dashboard')

        return Response({'status': 'complaint resolved'})


class WebsiteFeedbackViewSet(viewsets.ModelViewSet):
    queryset = WebsiteFeedback.objects.all()
    serializer_class = WebsiteFeedbackSerializer

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("You must be logged in to submit feedback.")
        serializer.save(user=self.request.user)


# ====================== HTML VIEWS ======================

def home(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='KSEB').exists():
            return redirect('complaints:kseb_dashboard')
        return redirect('complaints:report')
    return render(request, 'home.html')


@login_required
def report_complaint(request):
    if request.user.groups.filter(name='KSEB').exists():
        messages.error(request, "KSEB Admins cannot submit complaints.")
        return redirect('complaints:kseb_dashboard')

    if request.method == 'POST':
        type_ = request.POST.get('type')
        district = request.POST.get('district')
        place = request.POST.get('place')
        location = request.POST.get('location')
        issue = request.POST.get('issue')
        description = request.POST.get('description', '')
        phone = request.POST.get('phone')
        photo = request.FILES.get('photo')

        complaint = Complaint.objects.create(
            user=request.user,
            type=type_,
            district=district,
            place=place,
            location=location,
            issue=issue,
            description=description,
            phone=phone,
            photo=photo,
            status='pending',
            submitted_at=timezone.now()
        )

        messages.success(request, f'Complaint #{complaint.id} submitted successfully!')
        send_mail(
            'Complaint Received – Street Light System',
            f'Dear {request.user.username},\n\n'
            f'Your complaint has been received.\n'
            f'Complaint ID: {complaint.id}\n'
            f'Issue: {issue}\n'
            f'Location: {place}, {district}\n'
            f'Phone: {phone}\n\n'
            f'Thank you for reporting!',
            'priyaslms@gmail.com',
            [request.user.email],
            fail_silently=True,
        )
        return redirect('complaints:my_complaints')

    return render(request, 'report.html')


@login_required
def submit_website_rating(request):
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 0))
        feedback = request.POST.get('feedback', '').strip()

        if rating < 1 or rating > 5:
            return JsonResponse({'success': False, 'error': 'Invalid rating'})

        # Create or update
        obj, created = WebsiteFeedback.objects.update_or_create(
            user=request.user,
            defaults={'rating': rating, 'feedback': feedback}
        )
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid method'})


@require_POST
@login_required
def submit_rating(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id, user=request.user)
    
    if complaint.status != 'resolved' or complaint.user_rating:
        return JsonResponse({'success': False, 'error': 'Cannot rate'})

    rating = request.POST.get('rating')
    review = request.POST.get('review', '').strip()

    if rating and 1 <= int(rating) <= 5:
        complaint.user_rating = int(rating)
        complaint.user_review = review
        complaint.rated_at = timezone.now()
        complaint.save()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid rating'})


@login_required
def my_complaints(request):
    complaints = Complaint.objects.filter(user=request.user).prefetch_related('replies').order_by('-submitted_at')
    return render(request, 'my_complaints.html', {'complaints': complaints})


@login_required
def kseb_dashboard(request):
    if not request.user.groups.filter(name='KSEB').exists():
        messages.error(request, "Access denied. KSEB staff only.")
        return redirect('complaints:home')

    complaints = Complaint.objects.prefetch_related('replies').all().order_by('-submitted_at')
    pending_count = complaints.filter(status='pending').count()
    accepted_count = complaints.filter(status='accepted').count()
    resolved_count = complaints.filter(status='resolved').count()
    total_count = complaints.count()

    context = {
        'complaints': complaints,
        'pending_count': pending_count,
        'accepted_count': accepted_count,
        'resolved_count': resolved_count,
        'total_count': total_count
    }
    return render(request, 'kseb_dashboard.html', context)


@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)

    if not request.user.groups.filter(name='KSEB').exists():
        messages.error(request, "Access denied.")
        return redirect('complaints:kseb_dashboard')

    # Mark user replies as viewed by admin
    complaint.replies.filter(sent_by_admin=False, viewed_by_admin=False).update(viewed_by_admin=True)

    replies = complaint.replies.all().order_by('sent_at')

    # ESSENTIAL FIX: Reset unread_replies count when admin views the chat
    if complaint.unread_replies > 0:
        complaint.unread_replies = 0
        complaint.save()

    if request.method == 'POST':
        form = ComplaintReplyForm(request.POST, request.FILES)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.complaint = complaint
            reply.sent_by_admin = True
            reply.save()

            send_mail(
                'Update on Your Complaint',
                f'Hello {complaint.user.username},\n\n'
                f'KSEB Admin has sent you a message regarding Complaint #{complaint.id}:\n\n'
                f'{reply.message}\n\n'
                f'Login to view: http://127.0.0.1:8000/my-complaints/',
                'priyaslms@gmail.com',
                [complaint.user.email],
                fail_silently=True
            )

            messages.success(request, "Reply sent to user!")
            return redirect('complaints:complaint_detail', pk=pk)
    else:
        form = ComplaintReplyForm()

    return render(request, 'complaint_detail.html', {
        'complaint': complaint,
        'replies': replies,
        'form': form
    })


# ====================== USER REPLY FROM MY COMPLAINTS ======================
class UserReplyView(LoginRequiredMixin, View):
    def post(self, request, pk):
        complaint = get_object_or_404(Complaint, pk=pk, user=request.user)
        message = request.POST.get('message')
        photo = request.FILES.get('photo')

        if not message:
            messages.error(request, "Message cannot be empty.")
            return redirect('complaints:my_complaints')

        ComplaintReply.objects.create(
            complaint=complaint,
            message=message,
            photo=photo,
            sent_by_admin=False
        )

        # INCREMENT UNREAD COUNT FOR ADMIN
        complaint.unread_replies += 1
        complaint.save()

        messages.success(request, "Your reply has been sent to KSEB Admin.")
        return redirect('complaints:my_complaints')


# ====================== AUTH VIEWS ======================

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        email = request.POST.get('email')

        if form.is_valid():
            user = form.save(commit=False)
            user.email = email
            user.save()

            users_group, _ = Group.objects.get_or_create(name='Users')
            user.groups.add(users_group)

            messages.success(request, 'Registration successful! Please login.')
            return render(request, 'auth.html', {
                'register_form': UserCreationForm(),
                'show_login': True
            })
        else:
            return render(request, 'auth.html', {
                'register_form': form,
                'show_register': True
            })

    return render(request, 'auth.html', {
        'register_form': UserCreationForm(),
        'show_register': True
    })


def kseb_admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username == 'kseb_admin' and password == 'kseb@123':
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email='kseb@admin.com',
                    first_name='KSEB',
                    last_name='Admin'
                )
                group, _ = Group.objects.get_or_create(name='KSEB')
                user.groups.add(group)
                user.is_staff = True
                user.save()

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, "Welcome, KSEB Admin!")
                return redirect('complaints:kseb_dashboard')
            else:
                messages.error(request, "Authentication failed.")
        else:
            messages.error(request, "Invalid credentials.")

    return render(request, 'kseb_login.html')