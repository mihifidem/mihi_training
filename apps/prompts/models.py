import re

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg
from django.utils import timezone
from django.utils.text import slugify


class CategoriaPrompt(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Categoria de prompts'
        verbose_name_plural = 'Categorias de prompts'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)


class SubcategoriaPrompt(models.Model):
    categoria = models.ForeignKey(
        CategoriaPrompt,
        on_delete=models.CASCADE,
        related_name='subcategorias',
    )
    nombre = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140)
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Subcategoria de prompts'
        verbose_name_plural = 'Subcategorias de prompts'
        ordering = ['categoria__nombre', 'nombre']
        constraints = [
            models.UniqueConstraint(
                fields=['categoria', 'slug'],
                name='uniq_subcategoria_prompt_categoria_slug',
            )
        ]

    def __str__(self):
        return f'{self.categoria.nombre} / {self.nombre}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)


class HashtagPrompt(models.Model):
    nombre = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=80, unique=True)

    class Meta:
        verbose_name = 'Hashtag de prompt'
        verbose_name_plural = 'Hashtags de prompts'
        ordering = ['nombre']

    def __str__(self):
        return f'#{self.nombre}'

    def save(self, *args, **kwargs):
        if self.nombre.startswith('#'):
            self.nombre = self.nombre[1:]
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)


class Prompt(models.Model):
    VISIBILIDAD_PUBLICA = 'publico'
    VISIBILIDAD_SEMIPUBLICA = 'semipublico'
    VISIBILIDAD_PRIVADA = 'privado'

    VISIBILIDAD_CHOICES = [
        (VISIBILIDAD_PUBLICA, 'Publico total'),
        (VISIBILIDAD_SEMIPUBLICA, 'Semipublico'),
        (VISIBILIDAD_PRIVADA, 'Privado - membresia premium'),
    ]

    titulo = models.CharField(max_length=220)
    slug = models.SlugField(max_length=240, unique=True)
    descripcion = models.TextField(
        blank=True,
        help_text='Descripcion breve del prompt y para que sirve.',
    )
    contenido = models.TextField(
        help_text='El texto del prompt. Usa {nombre_variable} para partes rellenables.',
    )
    variables_json = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            'Definicion de variables: '
            '[{"nombre": "tema", "descripcion": "El tema a tratar", "valor_defecto": "marketing"}]'
        ),
    )
    categoria = models.ForeignKey(
        CategoriaPrompt,
        on_delete=models.PROTECT,
        related_name='prompts',
    )
    subcategoria = models.ForeignKey(
        SubcategoriaPrompt,
        on_delete=models.PROTECT,
        related_name='prompts',
        null=True,
        blank=True,
    )
    hashtags = models.ManyToManyField(HashtagPrompt, blank=True, related_name='prompts')
    visibilidad = models.CharField(
        max_length=20,
        choices=VISIBILIDAD_CHOICES,
        default=VISIBILIDAD_PUBLICA,
    )
    publicado = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)
    publicado_en = models.DateTimeField(default=timezone.now)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Prompt'
        verbose_name_plural = 'Prompts'
        ordering = ['-destacado', '-publicado_en']

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.titulo)
            slug = base
            n = 1
            while Prompt.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{n}'
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def tiene_variables(self):
        return bool(re.search(r'\{[^}]+\}', self.contenido))

    @property
    def nombres_variables(self):
        return re.findall(r'\{([^}]+)\}', self.contenido)

    @property
    def rating_promedio(self):
        data = self.valoraciones.aggregate(promedio=Avg('valor'))
        return data['promedio'] or 0


class ValoracionPrompt(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='valoraciones_prompts',
    )
    prompt = models.ForeignKey(
        Prompt,
        on_delete=models.CASCADE,
        related_name='valoraciones',
    )
    valor = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Valoracion de prompt'
        verbose_name_plural = 'Valoraciones de prompts'
        ordering = ['-creada_en']
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'prompt'],
                name='uniq_valoracion_prompt_usuario_prompt',
            )
        ]

    def __str__(self):
        return f'{self.usuario.username} - {self.prompt.titulo} ({self.valor})'


class PromptFavorito(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='prompts_favoritos',
    )
    prompt = models.ForeignKey(
        Prompt,
        on_delete=models.CASCADE,
        related_name='favoritos',
    )
    agregado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Prompt favorito'
        verbose_name_plural = 'Prompts favoritos'
        ordering = ['-agregado_en']
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'prompt'],
                name='uniq_favorito_prompt_usuario_prompt',
            )
        ]

    def __str__(self):
        return f'{self.usuario.username} - {self.prompt.titulo}'
