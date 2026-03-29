"""Views for the analytics app."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from datetime import timedelta

from apps.users.models import User, Notificacion
from apps.courses.models import Curso, Progreso, ResultadoQuiz, InscripcionCurso
from apps.gamification.models import InsigniaUsuario, Logro, LogroUsuario, Mision, MisionUsuario
from .forms import AsignarLogroForm, EnviarMensajeForm, AsignarMisionForm
from .models import RegistroActividad


class DashboardAdminView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Admin-only analytics dashboard."""
    template_name = 'analytics/dashboard_admin.html'

    def test_func(self):
        return self.request.user.is_staff

    def post(self, request, *args, **kwargs):
        form_type = request.POST.get('form_type')

        if form_type == 'asignar_mision':
            form = AsignarMisionForm(request.POST)
            if form.is_valid():
                usuarios = form.cleaned_data['usuarios']
                mision = form.cleaned_data['mision']
                aplicar_puntos_ahora = form.cleaned_data['aplicar_puntos_ahora']

                total_asignados = 0
                for usuario in usuarios:
                    MisionUsuario.objects.create(usuario=usuario, mision=mision)
                    total_asignados += 1

                    detalle = f'Se te asigno la mision "{mision.titulo}".'
                    if aplicar_puntos_ahora and mision.puntos_recompensa != 0:
                        usuario.agregar_puntos(mision.puntos_recompensa)
                        if mision.puntos_recompensa > 0:
                            detalle += f' Recibiste {mision.puntos_recompensa} puntos.'
                        else:
                            detalle += f' Se aplico una penalizacion de {abs(mision.puntos_recompensa)} puntos.'

                    Notificacion.objects.create(
                        usuario=usuario,
                        tipo='mision',
                        titulo='Nueva mision asignada',
                        mensaje=detalle,
                    )

                messages.success(
                    request,
                    f'Mision "{mision.titulo}" asignada a {total_asignados} alumno(s).',
                )
                return redirect('analytics:dashboard_admin')

            context = self.get_context_data()
            context['asignar_mision_form'] = form
            context['asignar_logro_form'] = AsignarLogroForm()
            context['enviar_mensaje_form'] = EnviarMensajeForm(request_user=request.user)
            return self.render_to_response(context)

        if form_type == 'asignar_logro':
            form = AsignarLogroForm(request.POST)
            if form.is_valid():
                usuario = form.cleaned_data['usuario']
                logro = form.cleaned_data['logro']
                puntos_asignados = form.cleaned_data['puntos_asignados']

                logro_usuario, created = LogroUsuario.objects.get_or_create(
                    usuario=usuario,
                    logro=logro,
                    defaults={'puntos_asignados': puntos_asignados},
                )

                if created:
                    usuario.agregar_puntos(puntos_asignados)
                    messages.success(
                        request,
                        f'Logro "{logro.nombre}" asignado a {usuario.username} con {puntos_asignados} puntos.',
                    )
                else:
                    messages.warning(
                        request,
                        f'{usuario.username} ya tiene el logro "{logro.nombre}" asignado.',
                    )
                return redirect('analytics:dashboard_admin')

            context = self.get_context_data()
            context['asignar_logro_form'] = form
            context['asignar_mision_form'] = AsignarMisionForm()
            context['enviar_mensaje_form'] = EnviarMensajeForm(request_user=request.user)
            return self.render_to_response(context)

        if form_type == 'enviar_mensaje':
            form = EnviarMensajeForm(request.POST, request_user=request.user)
            if form.is_valid():
                usuario = form.cleaned_data['usuario']
                titulo = form.cleaned_data['titulo']
                mensaje_texto = form.cleaned_data['mensaje']

                Notificacion.objects.create(
                    usuario=usuario,
                    tipo='sistema',
                    titulo=titulo,
                    mensaje=mensaje_texto,
                )
                messages.success(request, f'Mensaje enviado a {usuario.username}.')
                return redirect('analytics:dashboard_admin')

            context = self.get_context_data()
            context['asignar_logro_form'] = AsignarLogroForm()
            context['asignar_mision_form'] = AsignarMisionForm()
            context['enviar_mensaje_form'] = form
            return self.render_to_response(context)

        messages.error(request, 'No se pudo procesar la solicitud.')
        return redirect('analytics:dashboard_admin')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        last_30 = now - timedelta(days=30)

        context['total_usuarios'] = User.objects.filter(is_active=True, is_staff=False).count()
        context['total_cursos'] = Curso.objects.filter(activo=True).count()
        context['total_inscripciones'] = InscripcionCurso.objects.count()
        context['nuevos_usuarios_30d'] = User.objects.filter(
            date_joined__gte=last_30, is_staff=False
        ).count()

        # Most difficult topics (highest failure rate in quizzes)
        context['temas_dificiles'] = (
            ResultadoQuiz.objects
            .values('quiz__tema__titulo')
            .annotate(
                total=Count('id'),
                fallos=Count('id', filter=Q(aprobado=False)),
            )
            .filter(total__gte=3)
            .order_by('-fallos')[:5]
        )

        # Top 10 students by points
        context['top_alumnos'] = (
            User.objects.filter(is_active=True, is_staff=False)
            .order_by('-puntos')[:10]
        )

        # Activity last 30 days
        context['actividades_recientes'] = RegistroActividad.objects.filter(
            timestamp__gte=last_30
        ).select_related('usuario').order_by('-timestamp')[:30]

        # Courses by enrollment
        context['cursos_populares'] = (
            Curso.objects.annotate(inscritos=Count('inscripciones'))
            .order_by('-inscritos')[:5]
        )

        context['logros_creados'] = Logro.objects.select_related('insignia').order_by('nombre')
        context['asignar_logro_form'] = context.get('asignar_logro_form') or AsignarLogroForm()
        context['asignar_mision_form'] = context.get('asignar_mision_form') or AsignarMisionForm()
        context['misiones_activas_catalogo'] = Mision.objects.filter(activa=True).order_by('titulo')[:8]
        context['enviar_mensaje_form'] = context.get('enviar_mensaje_form') or EnviarMensajeForm(
            request_user=self.request.user
        )

        return context


class ProgresoAlumnoView(LoginRequiredMixin, TemplateView):
    """Personal progress analytics for the logged-in student."""
    template_name = 'analytics/progreso_alumno.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        inscripciones = InscripcionCurso.objects.filter(usuario=user).select_related('curso')
        progreso_por_curso = []
        for insc in inscripciones:
            total = insc.curso.temas.count()
            completados = Progreso.objects.filter(
                usuario=user, tema__curso=insc.curso, completado=True
            ).count()
            pct = int((completados / total) * 100) if total else 0
            progreso_por_curso.append({
                'curso': insc.curso,
                'completados': completados,
                'total': total,
                'porcentaje': pct,
                'completado': insc.completado,
            })

        context['progreso_cursos'] = progreso_por_curso
        context['actividades'] = RegistroActividad.objects.filter(usuario=user)[:20]
        context['resultados_quiz'] = ResultadoQuiz.objects.filter(
            usuario=user
        ).select_related('quiz__tema__curso').order_by('-fecha')[:10]
        return context
