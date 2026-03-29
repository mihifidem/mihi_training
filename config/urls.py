"""Main URL configuration."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Redirect root to dashboard (or login if not authenticated)
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),

    # App URLs
    path('dashboard/', include('apps.users.urls', namespace='users')),
    path('cursos/', include('apps.courses.urls', namespace='courses')),
    path('gamificacion/', include('apps.gamification.urls', namespace='gamification')),
    path('recompensas/', include('apps.rewards.urls', namespace='rewards')),
    path('analytics/', include('apps.analytics.urls', namespace='analytics')),
    path('certificados/', include('apps.certifications.urls', namespace='certifications')),
    path('tutor/', include('apps.ai_tutor.urls', namespace='ai_tutor')),
    path('enlaces/', include('apps.enlaces.urls', namespace='enlaces')),

    # API
    path('api/v1/', include('apps.api.urls')),

    # django-allauth (login, register, social auth)
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
