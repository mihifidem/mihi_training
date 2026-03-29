"""Models for the courses app."""
import os

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


class TipoCurso(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Tipo de curso'
        verbose_name_plural = 'Tipos de curso'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Curso(models.Model):
    tipo_curso = models.ForeignKey(
        TipoCurso,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cursos',
    )
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='cursos/', null=True, blank=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    horas_duracion = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['-destacado', '-creado_en']

    def __str__(self):
        return self.nombre

    @property
    def total_temas(self):
        return self.temas.count()


class Tema(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='temas')
    titulo = models.CharField(max_length=200)
    contenido = models.TextField(help_text='Soporta Markdown / HTML')
    orden = models.PositiveIntegerField(default=0)
    puntos_otorgados = models.PositiveIntegerField(default=10)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Tema'
        verbose_name_plural = 'Temas'
        ordering = ['orden']

    def __str__(self):
        return f'[{self.curso.nombre}] {self.titulo}'


class TipoRecursoTema(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=50, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Tipo de recurso'
        verbose_name_plural = 'Tipos de recurso'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class TemaRecurso(models.Model):
    PUNTOS_VISUALIZACION = 3

    tema = models.ForeignKey(Tema, on_delete=models.CASCADE, related_name='recursos')
    titulo = models.CharField(max_length=200)
    archivo = models.FileField(upload_to='recursos_tema/')
    tipo_recurso = models.ForeignKey(
        TipoRecursoTema,
        on_delete=models.PROTECT,
        related_name='recursos',
    )
    orden = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Recurso de tema'
        verbose_name_plural = 'Recursos de tema'
        ordering = ['orden', 'titulo']

    def __str__(self):
        return f'{self.tema.titulo} — {self.titulo}'

    def clean(self):
        super().clean()
        if not self.archivo or not self.tipo_recurso_id:
            return
        extension = os.path.splitext(self.archivo.name)[1].lower()
        extensiones_validas = {
            'pdf': {'.pdf'},
            'audio': {'.mp3', '.wav', '.ogg', '.m4a'},
            'video': {'.mp4', '.webm', '.mov', '.m4v'},
            'imagen': {'.png', '.jpg', '.jpeg', '.gif', '.webp'},
        }
        extensiones_permitidas = extensiones_validas.get(self.tipo_codigo)
        if extensiones_permitidas and extension not in extensiones_permitidas:
            extensiones = ', '.join(sorted(extensiones_permitidas))
            raise ValidationError({
                'archivo': f'El archivo debe tener una extensión válida ({extensiones}) para recursos de tipo {self.tipo_nombre}.'
            })

    @property
    def tipo_codigo(self):
        return self.tipo_recurso.codigo

    @property
    def tipo_nombre(self):
        return self.tipo_recurso.nombre


class TemaRecursoVisualizacion(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='visualizaciones_recursos_tema',
    )
    recurso = models.ForeignKey(
        TemaRecurso,
        on_delete=models.CASCADE,
        related_name='visualizaciones',
    )
    puntos_otorgados = models.PositiveIntegerField(default=TemaRecurso.PUNTOS_VISUALIZACION)
    vista_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'recurso')
        verbose_name = 'Visualización de recurso'
        verbose_name_plural = 'Visualizaciones de recursos'
        ordering = ['-vista_en']

    def __str__(self):
        return f'{self.usuario.username} — {self.recurso.titulo}'


class InscripcionCurso(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inscripciones'
    )
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='inscripciones')
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    completado = models.BooleanField(default=False)
    fecha_completado = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('usuario', 'curso')
        verbose_name = 'Inscripción'
        verbose_name_plural = 'Inscripciones'

    def __str__(self):
        return f'{self.usuario.username} → {self.curso.nombre}'


class Progreso(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progresos'
    )
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE, related_name='progresos')
    completado = models.BooleanField(default=False)
    fecha_completado = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('usuario', 'tema')
        verbose_name = 'Progreso'
        verbose_name_plural = 'Progresos'

    def __str__(self):
        estado = '✓' if self.completado else '○'
        return f'{estado} {self.usuario.username} — {self.tema.titulo}'

    def marcar_completado(self):
        if not self.completado:
            self.completado = True
            self.fecha_completado = timezone.now()
            self.save(update_fields=['completado', 'fecha_completado'])


# ---------------------------------------------------------------------------
# Quizzes
# ---------------------------------------------------------------------------

class Quiz(models.Model):
    tema = models.OneToOneField(Tema, on_delete=models.CASCADE, related_name='quiz')
    titulo = models.CharField(max_length=200)
    csv_filename = models.CharField(
        max_length=255,
        blank=True,
        help_text='Nombre del CSV dentro de static/quiz (ej: 0201QZ.csv).',
    )
    puntos_bonus = models.PositiveIntegerField(default=20)
    porcentaje_aprobacion = models.PositiveIntegerField(
        default=70, help_text='Porcentaje mínimo para aprobar (0-100)'
    )

    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'

    def __str__(self):
        return self.titulo


class Pregunta(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='preguntas')
    texto = models.TextField()
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['orden']
        verbose_name = 'Pregunta'
        verbose_name_plural = 'Preguntas'

    def __str__(self):
        return self.texto[:80]


class Respuesta(models.Model):
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE, related_name='respuestas')
    texto = models.CharField(max_length=500)
    es_correcta = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Respuesta'
        verbose_name_plural = 'Respuestas'

    def __str__(self):
        marca = '✓' if self.es_correcta else '✗'
        return f'{marca} {self.texto[:60]}'


class ResultadoQuiz(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resultados_quiz'
    )
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='resultados')
    puntuacion = models.PositiveIntegerField(default=0)
    total_preguntas = models.PositiveIntegerField(default=0)
    fecha = models.DateTimeField(auto_now_add=True)
    aprobado = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Resultado Quiz'
        verbose_name_plural = 'Resultados Quiz'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.usuario.username} — {self.quiz.titulo} ({self.puntuacion}/{self.total_preguntas})'

    @property
    def porcentaje(self):
        if self.total_preguntas == 0:
            return 0
        return int((self.puntuacion / self.total_preguntas) * 100)


# ---------------------------------------------------------------------------
# Learning path
# ---------------------------------------------------------------------------

class RutaAprendizaje(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ruta'
    )
    cursos_recomendados = models.ManyToManyField(Curso, blank=True, related_name='rutas')
    tema_actual = models.ForeignKey(
        Tema, on_delete=models.SET_NULL, null=True, blank=True, related_name='rutas_actuales'
    )
    actualizada_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ruta de Aprendizaje'
        verbose_name_plural = 'Rutas de Aprendizaje'

    def __str__(self):
        return f'Ruta de {self.usuario.username}'
