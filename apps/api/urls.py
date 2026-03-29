"""Unified API router — registers all app ViewSets."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

# Import ViewSets from each app
from apps.users.views import UserViewSet, NotificacionViewSet
from apps.courses.views import CursoViewSet, TemaViewSet, ResultadoQuizViewSet
from apps.gamification.views import InsigniaViewSet, MisionUsuarioViewSet
from apps.rewards.views import RecompensaViewSet, CanjeViewSet
from apps.certifications.views import CertificadoViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'notifications', NotificacionViewSet, basename='notificacion')
router.register(r'courses', CursoViewSet, basename='curso')
router.register(r'topics', TemaViewSet, basename='tema')
router.register(r'quiz-results', ResultadoQuizViewSet, basename='resultado_quiz')
router.register(r'badges', InsigniaViewSet, basename='insignia')
router.register(r'missions', MisionUsuarioViewSet, basename='mision_usuario')
router.register(r'rewards', RecompensaViewSet, basename='recompensa')
router.register(r'redemptions', CanjeViewSet, basename='canje')
router.register(r'certificates', CertificadoViewSet, basename='certificado')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
    # OpenAPI schema & docs
    path('schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api-schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='api-schema'), name='redoc'),
]
