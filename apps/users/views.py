"""Views for the users app — both HTML and API ViewSets."""
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.db.models import Avg, Count
from django.views.generic import (
    CreateView, DetailView, UpdateView, TemplateView, View, ListView
)
from django.http import JsonResponse

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import User, Notificacion
from .forms import RegistroForm, PerfilForm
from .serializers import UserSerializer, NotificacionSerializer


class LandingView(TemplateView):
    """Public landing page with blog highlights."""
    template_name = 'landing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.blog.models import PostBlog

        context['posts_destacados'] = (
            PostBlog.objects.filter(
                publicado=True,
                visibilidad=PostBlog.VISIBILIDAD_PUBLICA,
            )
            .select_related('categoria', 'subcategoria')
            .prefetch_related('hashtags')
            .annotate(promedio_rating=Avg('valoraciones__valor'), total_valoraciones=Count('valoraciones'))
            .order_by('-destacado', '-publicado_en')[:9]
        )
        return context


# ---------------------------------------------------------------------------
# HTML Views
# ---------------------------------------------------------------------------

class RegistroView(CreateView):
    """User registration page."""
    form_class = RegistroForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:dashboard')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(self.request, f'¡Bienvenido/a {user.first_name}! Tu cuenta ha sido creada.')
        return redirect(self.success_url)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('users:dashboard')
        return super().dispatch(request, *args, **kwargs)


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main user dashboard."""
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        from apps.courses.models import InscripcionCurso, Progreso
        from apps.gamification.models import InsigniaUsuario, LogroUsuario, MisionUsuario
        from apps.rewards.models import CanjeRecompensa
        from apps.blog.models import LecturaPostUsuario

        inscripciones = InscripcionCurso.objects.filter(
            usuario=user
        ).select_related('curso')[:5]

        insignias_recientes = InsigniaUsuario.objects.filter(
            usuario=user
        ).select_related('insignia').order_by('-fecha_obtenida')[:6]

        misiones_activas = MisionUsuario.objects.filter(
            usuario=user, completada=False
        ).select_related('mision')[:5]

        logros_recientes = LogroUsuario.objects.filter(
            usuario=user
        ).select_related('logro').order_by('-fecha_obtenido')[:6]

        canjes_recientes = CanjeRecompensa.objects.filter(
            usuario=user
        ).select_related('recompensa').order_by('-fecha_canje')[:6]

        lecturas_posts = LecturaPostUsuario.objects.filter(
            usuario=user
        ).select_related('post').order_by('-iniciada_en')[:8]

        total_posts_vistos = LecturaPostUsuario.objects.filter(usuario=user).count()
        total_posts_con_puntos = LecturaPostUsuario.objects.filter(
            usuario=user,
            puntos_otorgados=True,
        ).count()

        actividades = user.actividades.order_by('-timestamp')[:10]

        context.update({
            'inscripciones': inscripciones,
            'insignias_recientes': insignias_recientes,
            'logros_recientes': logros_recientes,
            'canjes_recientes': canjes_recientes,
            'misiones_activas': misiones_activas,
            'actividades': actividades,
            'lecturas_posts': lecturas_posts,
            'total_posts_vistos': total_posts_vistos,
            'total_posts_con_puntos': total_posts_con_puntos,
        })
        return context


class PerfilView(LoginRequiredMixin, DetailView):
    """Public profile page."""
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'perfil'

    def get_object(self, queryset=None):
        username = self.kwargs.get('username', self.request.user.username)
        from django.shortcuts import get_object_or_404
        return get_object_or_404(User, username=username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        perfil = self.get_object()
        from apps.gamification.utils import get_insignias_activas_ids, get_insignias_visibles_para_usuario
        from apps.certifications.models import Certificado

        insignias_list = list(get_insignias_visibles_para_usuario(perfil))
        activas_ids = get_insignias_activas_ids(perfil)
        context['insignias_con_estado'] = [(insignia, insignia.id in activas_ids) for insignia in insignias_list]
        context['total_insignias'] = len(insignias_list)
        context['total_insignias_activas'] = sum(1 for insignia in insignias_list if insignia.id in activas_ids)
        context['certificados'] = Certificado.objects.filter(usuario=perfil)
        return context


class EditarPerfilView(LoginRequiredMixin, UpdateView):
    """Edit own profile."""
    model = User
    form_class = PerfilForm
    template_name = 'users/edit_profile.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('users:perfil', kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        messages.success(self.request, 'Perfil actualizado correctamente.')
        return super().form_valid(form)


class NotificacionesView(LoginRequiredMixin, ListView):
    """Notification centre."""
    model = Notificacion
    template_name = 'users/notificaciones.html'
    context_object_name = 'notificaciones'
    paginate_by = 20

    def get_queryset(self):
        return Notificacion.objects.filter(usuario=self.request.user)


class MarcarNotificacionLeidaView(LoginRequiredMixin, View):
    def post(self, request, pk=None):
        if pk:
            notif = Notificacion.objects.filter(pk=pk, usuario=request.user).first()
            if notif:
                notif.leida = not notif.leida
                notif.save(update_fields=['leida'])
        else:
            Notificacion.objects.filter(usuario=request.user, leida=False).update(leida=True)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'ok': True})
        return redirect('users:notificaciones')


# ---------------------------------------------------------------------------
# DRF ViewSets (used via apps/api/urls.py)
# ---------------------------------------------------------------------------

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(is_active=True)

    @action(detail=False, methods=['get'])
    def me(self, request):
        return Response(UserSerializer(request.user).data)


class NotificacionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificacionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notificacion.objects.filter(usuario=self.request.user)

    @action(detail=True, methods=['post'])
    def marcar_leida(self, request, pk=None):
        notif = self.get_object()
        notif.leida = True
        notif.save(update_fields=['leida'])
        return Response({'ok': True})
