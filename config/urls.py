"""Main URL configuration."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.users.views import LandingView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Public landing page
    path('', LandingView.as_view(), name='landing'),

    # App URLs
    path('dashboard/', include('apps.users.urls', namespace='users')),
    path('cursos/', include('apps.courses.urls', namespace='courses')),
    path('blog/', include('apps.blog.urls', namespace='blog')),
    path('gamificacion/', include('apps.gamification.urls', namespace='gamification')),
    path('recompensas/', include('apps.rewards.urls', namespace='rewards')),
    path('analytics/', include('apps.analytics.urls', namespace='analytics')),
    path('certificados/', include('apps.certifications.urls', namespace='certifications')),
    path('tutor/', include('apps.ai_tutor.urls', namespace='ai_tutor')),
    path('enlaces/', include('apps.enlaces.urls', namespace='enlaces')),
    path('prompts/', include('apps.prompts.urls', namespace='prompts')),

    # API
    path('api/v1/', include('apps.api.urls')),

    # django-allauth (login, register, social auth)
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
