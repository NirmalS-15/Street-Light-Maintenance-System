# complaints/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import Complaint, ComplaintReply, WebsiteFeedback


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'issue', 'place', 'status', 'rating_meter', 'submitted_at')
    list_filter = ('status', 'district', 'type', 'user_rating')
    search_fields = ('issue', 'place', 'user__username', 'user_review')
    readonly_fields = (
        'user', 'type', 'district', 'place', 'location', 'issue', 'description', 'phone', 'photo',
        'status', 'submitted_at', 'accepted_at', 'resolved_at', 'resolution_notes', 'resolution_image',
        'user_rating', 'user_review', 'rated_at',
        'show_user_rating_meter'  # Text meter at bottom
    )

    # LIST VIEW: Text meter (Good, Bad, etc.)
    def rating_meter(self, obj):
        if obj.user_rating:
            meter = self.get_rating_text(obj.user_rating)
            color = {
                1: '#dc3545',  # red
                2: '#fd7e14',  # orange
                3: '#ffc107',  # yellow
                4: '#28a745',  # green
                5: '#20c997'   # teal
            }.get(obj.user_rating, '#6c757d')
            return format_html(
                '<span style="color:{}; font-weight:bold; font-size:0.95rem;">{}</span>',
                color, meter
            )
        return format_html('<span style="color:#999; font-style:italic;">Not rated</span>')
    rating_meter.short_description = 'Rating'
    rating_meter.allow_tags = True

    def get_rating_text(self, rating):
        return {
            1: 'Very Poor',
            2: 'Poor',
            3: 'Average',
            4: 'Good',
            5: 'Excellent!'
        }.get(rating, 'Unknown')

    # DETAIL VIEW: Clean text meter at bottom
    def show_user_rating_meter(self, obj):
        if not obj.user_rating:
            return format_html(
                '<div style="padding:16px; background:#f8f9fa; border-radius:10px; text-align:center; color:#999; font-style:italic;">'
                'User has not rated yet.'
                '</div>'
            )

        meter = self.get_rating_text(obj.user_rating)
        color = {
            1: '#dc3545', 2: '#fd7e14', 3: '#ffc107', 4: '#28a745', 5: '#20c997'
        }.get(obj.user_rating, '#6c757d')
        review = obj.user_review or "No review provided"
        rated_at = obj.rated_at.strftime("%d %b %Y, %I:%M %p") if obj.rated_at else "Unknown"

        return format_html(
            '''
            <div style="
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 12px;
                padding: 18px;
                margin: 20px 0;
                text-align: center;
                font-family: 'Segoe UI', sans-serif;
            ">
                <h5 style="margin:0 0 10px; color:#212529; font-weight:600;">
                    User Feedback
                </h5>
                <p style="margin:8px 0; color:{}; font-weight:bold; font-size:1.3rem;">
                    {}
                </p>
                <p style="margin:10px auto; color:#495057; font-style:italic; font-size:1rem; max-width:500px; line-height:1.5;">
                    "{}"
                </p>
                <small style="color:#6c757d;">
                    Rated on {}
                </small>
            </div>
            ''',
            color, meter, review, rated_at
        )
    show_user_rating_meter.short_description = "User Rating & Review"

    # ORGANIZE DETAIL VIEW
    fieldsets = (
        ('User & Location', {
            'fields': ('user', 'type', 'district', 'place', 'location', 'phone')
        }),
        ('Complaint Details', {
            'fields': ('issue', 'description', 'photo')
        }),
        ('Status & Timeline', {
            'fields': ('status', 'submitted_at', 'accepted_at', 'resolved_at')
        }),
        ('Resolution', {
            'fields': ('resolution_notes', 'resolution_image')
        }),
        ('User Feedback', {
            'fields': ('user_rating', 'user_review', 'rated_at', 'show_user_rating_meter'),
            'classes': ('collapse',),
        }),
    )