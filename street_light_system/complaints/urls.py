# complaints/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
app_name = 'complaints'

urlpatterns = [
    # === HTML Views ===
    path('', views.home, name='home'),                         # Home page
    path('report/', views.report_complaint, name='report'),    # Submit complaint
    path('my-complaints/', views.my_complaints, name='my_complaints'),
    # === Auth ===
    path('register/', views.register, name='register'),
    path('kseb-login/', views.kseb_admin_login, name='kseb_login'),
    path('kseb-dashboard/', views.kseb_dashboard, name='kseb_dashboard'),  # ADD THIS
    path('api/complaints/<int:pk>/accept/', views.ComplaintViewSet.as_view({'post': 'accept'}), name='complaint_accept'),
    path('api/complaints/<int:pk>/resolve/', views.ComplaintViewSet.as_view({'post': 'resolve'}), name='complaint_resolve'),
    path('complaint/<int:pk>/', views.complaint_detail, name='complaint_detail'),
    # complaints/urls.py

    path('submit-website-rating/', views.submit_website_rating, name='submit_website_rating'),
    # complaints/urls.py
    path('submit-rating/<int:complaint_id>/', views.submit_rating, name='submit_rating'),
    path('logout/', auth_views.LogoutView.as_view(
        template_name='home.html',  # Optional: show message
        next_page='complaints:home'
    ), name='logout'),
    # complaints/urls.py
    path('complaints/<int:pk>/reply/', views.UserReplyView.as_view(), name='user_reply'),
]