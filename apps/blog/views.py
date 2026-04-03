from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Avg
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView

from apps.analytics.models import RegistroActividad

from .models import (
    CategoriaBlog,
    HashtagBlog,
    LecturaPostUsuario,
    PostBlog,
    SubcategoriaBlog,
    ValoracionPost,
)


def _es_premium(usuario):
    if not usuario.is_authenticated:
        return False
    return usuario.is_staff or usuario.role == 'premium'


def _es_usuario_registrado_valido(usuario):
    if not usuario.is_authenticated:
        return False
    if usuario.is_staff:
        return True
    # freemium se mapea al rol "basic" del proyecto.
    return usuario.role in {'alumno', 'basic', 'freemium', 'premium'}


def _puede_ver_post(usuario, post):
    if post.visibilidad == PostBlog.VISIBILIDAD_PUBLICA:
        return True
    if post.visibilidad == PostBlog.VISIBILIDAD_SEMIPUBLICA:
        return _es_usuario_registrado_valido(usuario)
    if post.visibilidad == PostBlog.VISIBILIDAD_PRIVADA:
        return _es_usuario_registrado_valido(usuario)
    return False


def _posts_visibles_para_usuario(usuario):
    queryset = PostBlog.objects.filter(
        publicado=True,
        publicado_en__lte=timezone.now(),
    )
    if _es_usuario_registrado_valido(usuario):
        return queryset
    return queryset.filter(visibilidad=PostBlog.VISIBILIDAD_PUBLICA)


class BlogListView(ListView):
    template_name = 'blog/list.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        queryset = (
            _posts_visibles_para_usuario(self.request.user)
            .select_related('categoria', 'subcategoria')
            .prefetch_related('hashtags')
            .annotate(promedio_rating=Avg('valoraciones__valor'), total_valoraciones=Count('valoraciones'))
            .order_by('-destacado', '-publicado_en')
        )

        q = (self.request.GET.get('q') or '').strip()
        categoria = (self.request.GET.get('categoria') or '').strip()
        subcategoria = (self.request.GET.get('subcategoria') or '').strip()
        hashtag = (self.request.GET.get('hashtag') or '').strip()

        if q:
            queryset = queryset.filter(
                Q(titulo__icontains=q)
                | Q(resumen__icontains=q)
                | Q(contenido_publico__icontains=q)
                | Q(contenido_privado__icontains=q)
            )
        if categoria:
            queryset = queryset.filter(categoria__slug=categoria)
        if subcategoria:
            queryset = queryset.filter(subcategoria__slug=subcategoria)
        if hashtag:
            queryset = queryset.filter(hashtags__slug=hashtag)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q_actual'] = (self.request.GET.get('q') or '').strip()
        context['categoria_actual'] = (self.request.GET.get('categoria') or '').strip()
        context['subcategoria_actual'] = (self.request.GET.get('subcategoria') or '').strip()
        context['hashtag_actual'] = (self.request.GET.get('hashtag') or '').strip()

        visibles = _posts_visibles_para_usuario(self.request.user)

        context['categorias'] = CategoriaBlog.objects.filter(activa=True).order_by('nombre')
        context['subcategorias'] = SubcategoriaBlog.objects.filter(activa=True).order_by('nombre')
        context['hashtags'] = HashtagBlog.objects.all().order_by('nombre')

        context['grupos_categorias'] = (
            CategoriaBlog.objects.filter(activa=True)
            .annotate(total_posts=Count('posts', filter=Q(posts__in=visibles)))
            .prefetch_related('subcategorias')
            .order_by('nombre')
        )
        context['grupos_subcategorias'] = (
            SubcategoriaBlog.objects.filter(activa=True)
            .annotate(total_posts=Count('posts', filter=Q(posts__in=visibles)))
            .select_related('categoria')
            .order_by('categoria__nombre', 'nombre')
        )
        context['grupos_hashtags'] = (
            HashtagBlog.objects.annotate(total_posts=Count('posts', filter=Q(posts__in=visibles)))
            .order_by('-total_posts', 'nombre')
        )
        context['es_premium'] = _es_premium(self.request.user)
        return context


class BlogDetailView(DetailView):
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return (
            _posts_visibles_para_usuario(self.request.user)
            .select_related('categoria', 'subcategoria')
            .prefetch_related('hashtags')
            .annotate(promedio_rating=Avg('valoraciones__valor'), total_valoraciones=Count('valoraciones'))
        )

    def get_object(self, queryset=None):
        return get_object_or_404(self.get_queryset(), slug=self.kwargs['slug'])

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if not _puede_ver_post(request.user, post):
            if request.user.is_authenticated:
                messages.error(request, 'No tienes permisos para ver este post.')
            else:
                messages.error(request, 'Debes iniciar sesion para ver este contenido.')
            return redirect('blog:list')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesion para valorar posts.')
            return redirect('account_login')

        post = self.get_object()
        try:
            valor = int(request.POST.get('valor', 0))
        except ValueError:
            valor = 0

        if valor < 1 or valor > 5:
            messages.error(request, 'La valoracion debe estar entre 1 y 5 duckies.')
            return redirect('blog:detail', slug=post.slug)

        ValoracionPost.objects.update_or_create(
            usuario=request.user,
            post=post,
            defaults={'valor': valor},
        )
        messages.success(request, 'Tu valoracion se guardo correctamente.')
        return redirect('blog:detail', slug=post.slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = context['post']
        usuario = self.request.user
        context['es_premium'] = _es_premium(usuario)
        context['puede_ver_privado'] = _puede_ver_post(usuario, post)

        if usuario.is_authenticated:
            valoracion_usuario = ValoracionPost.objects.filter(usuario=usuario, post=post).first()
            context['valoracion_usuario'] = valoracion_usuario.valor if valoracion_usuario else 0

            lectura = LecturaPostUsuario.objects.filter(usuario=usuario, post=post).first()
            context['lectura_completada'] = bool(lectura and lectura.puntos_otorgados)
        else:
            context['valoracion_usuario'] = 0
            context['lectura_completada'] = False

        context['puntos_lectura'] = post.puntos_lectura
        context['segundos_requeridos'] = post.segundos_objetivo

        if usuario.is_authenticated:
            self.request.session[f'blog_post_inicio_{post.id}'] = timezone.now().isoformat()
        return context


class RegistrarLecturaCompletaView(LoginRequiredMixin, View):
    def post(self, request, slug):
        post = get_object_or_404(_posts_visibles_para_usuario(request.user), slug=slug)

        if post.visibilidad == PostBlog.VISIBILIDAD_PRIVADA and not _es_premium(request.user):
            return JsonResponse({'ok': False, 'error': 'No autorizado.'}, status=403)

        session_key = f'blog_post_inicio_{post.id}'
        inicio_raw = request.session.get(session_key)
        if not inicio_raw:
            return JsonResponse({'ok': False, 'error': 'No se registro inicio de lectura.'}, status=400)

        try:
            inicio = datetime.fromisoformat(inicio_raw)
            if timezone.is_naive(inicio):
                inicio = timezone.make_aware(inicio, timezone.get_current_timezone())
        except ValueError:
            return JsonResponse({'ok': False, 'error': 'Marca de tiempo invalida.'}, status=400)

        transcurridos = int((timezone.now() - inicio).total_seconds())
        segundos_minimos = post.segundos_objetivo
        if transcurridos < segundos_minimos:
            return JsonResponse(
                {
                    'ok': False,
                    'completo': False,
                    'faltan_segundos': segundos_minimos - transcurridos,
                },
                status=400,
            )

        lectura, creada = LecturaPostUsuario.objects.get_or_create(
            usuario=request.user,
            post=post,
            defaults={'iniciada_en': inicio},
        )

        if not lectura.puntos_otorgados:
            request.user.agregar_puntos(post.puntos_lectura)
            lectura.puntos_otorgados = True
            lectura.completada_en = timezone.now()
            if creada:
                lectura.iniciada_en = inicio
            lectura.save(update_fields=['iniciada_en', 'completada_en', 'puntos_otorgados'])
            RegistroActividad.objects.create(
                usuario=request.user,
                tipo='acceso',
                descripcion=f'Lectura completada del post: {post.titulo}',
                puntos_ganados=post.puntos_lectura,
            )
            request.session.pop(session_key, None)
            return JsonResponse(
                {
                    'ok': True,
                    'completo': True,
                    'puntos_ganados': post.puntos_lectura,
                    'puntos_totales': request.user.puntos_totales,
                }
            )

        return JsonResponse({'ok': True, 'completo': True, 'puntos_ganados': 0})
