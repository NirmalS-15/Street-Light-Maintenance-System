# street_light_system/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

# Import your views
from complaints.views import register, kseb_admin_login

# ---------- DRF Router ----------
from rest_framework import routers
from complaints import views as complaints_views

router = routers.DefaultRouter()
router.register(r'api/complaints', complaints_views.ComplaintViewSet, basename='complaint')
router.register(r'api/feedback', complaints_views.WebsiteFeedbackViewSet, basename='feedback')

# ---------- URL Patterns ----------
urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # === AUTH ===
    path('auth/', TemplateView.as_view(template_name='auth.html'), name='auth'),
    path('login/', auth_views.LoginView.as_view(template_name='auth.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='complaints:home'), name='logout'),
    path('register/', register, name='register'),

    # === KSEB ADMIN LOGIN ===
    path('kseb-admin-login/', kseb_admin_login, name='kseb_admin_login'),

    # === APP ROUTES (from complaints/urls.py) ===
    path('', include('complaints.urls')),

    # === DRF API ROUTES ===
    path('api/', include(router.urls)),
    path('logout/', auth_views.LogoutView.as_view(next_page='complaints:home'), name='logout'),

]

# ---------- Serve Media in Development ----------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)