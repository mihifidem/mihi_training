"""Models for the Curriculum Vitae builder app."""
from django.db import models
from django.conf import settings
from django.utils.text import slugify


class CurriculumVitae(models.Model):
    """Root container – one per user."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='curriculum',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Curriculum Vitae'
        verbose_name_plural = 'Curriculums Vitae'

    def __str__(self):
        return f'CV de {self.user.get_full_name() or self.user.username}'


# ─── Section 1: Personal info ─────────────────────────────────────────────────

DISPONIBILIDAD_CHOICES = [
    ('inmediata', 'Inmediata'),
    ('parcial', 'Parcial'),
    ('por_acordar', 'Por acordar'),
    ('no_disponible', 'No disponible'),
]


class PersonalInfo(models.Model):
    cv = models.OneToOneField(
        CurriculumVitae, on_delete=models.CASCADE, related_name='personal_info',
    )
    nombre = models.CharField('Nombre', max_length=100)
    apellidos = models.CharField('Apellidos', max_length=150)
    telefono1 = models.CharField('Teléfono 1', max_length=30)
    telefono2 = models.CharField('Teléfono 2', max_length=30, blank=True)
    email_profesional1 = models.EmailField('Email profesional 1')
    email_profesional2 = models.EmailField('Email profesional 2', blank=True)
    ciudad = models.CharField('Ciudad', max_length=100)
    pais = models.CharField('País', max_length=100)
    codigo_postal = models.CharField('Código postal', max_length=20, blank=True)
    fecha_nacimiento = models.DateField('Fecha de nacimiento', null=True, blank=True)
    nacionalidad = models.CharField('Nacionalidad', max_length=100, blank=True)
    carnet_conducir = models.BooleanField('Carnet de conducir', default=False)
    disponibilidad = models.CharField(
        'Disponibilidad', max_length=20, choices=DISPONIBILIDAD_CHOICES, default='inmediata',
    )
    foto = models.ImageField('Foto', upload_to='curriculum/fotos/', null=True, blank=True)

    class Meta:
        verbose_name = 'Datos personales'

    def __str__(self):
        return f'{self.nombre} {self.apellidos}'

    @property
    def nombre_completo(self):
        return f'{self.nombre} {self.apellidos}'


# ─── Section 2: Professional profile ─────────────────────────────────────────

class ProfessionalProfile(models.Model):
    cv = models.OneToOneField(
        CurriculumVitae, on_delete=models.CASCADE, related_name='professional_profile',
    )
    profesion = models.CharField('Profesión / Especialidad', max_length=200)
    objetivo = models.CharField('Objetivo profesional', max_length=300, blank=True)
    resumen = models.TextField('Resumen profesional')

    class Meta:
        verbose_name = 'Perfil profesional'

    def __str__(self):
        return self.profesion


# ─── Section 3: Work experience ───────────────────────────────────────────────

class WorkExperience(models.Model):
    cv = models.ForeignKey(
        CurriculumVitae, on_delete=models.CASCADE, related_name='work_experiences',
    )
    puesto = models.CharField('Puesto', max_length=200)
    empresa = models.CharField('Empresa', max_length=200)
    ubicacion = models.CharField('Ubicación', max_length=200, blank=True)
    fecha_inicio = models.DateField('Fecha inicio')
    fecha_fin = models.DateField('Fecha fin', null=True, blank=True)
    trabajo_actual = models.BooleanField('Trabajo actual', default=False)
    descripcion = models.TextField('Descripción / Responsabilidades', blank=True)
    logros = models.TextField('Logros', blank=True)
    orden = models.PositiveSmallIntegerField('Orden', default=0)

    class Meta:
        verbose_name = 'Experiencia laboral'
        verbose_name_plural = 'Experiencias laborales'
        ordering = ['orden', '-fecha_inicio']

    def __str__(self):
        return f'{self.puesto} en {self.empresa}'

    @property
    def periodo(self):
        fin = 'Actualidad' if self.trabajo_actual else (self.fecha_fin.strftime('%m/%Y') if self.fecha_fin else '')
        return f'{self.fecha_inicio.strftime("%m/%Y")} – {fin}'


# ─── Section 4: Academic education ───────────────────────────────────────────

class Education(models.Model):
    cv = models.ForeignKey(
        CurriculumVitae, on_delete=models.CASCADE, related_name='educations',
    )
    titulo = models.CharField('Título', max_length=200)
    centro = models.CharField('Centro educativo', max_length=200)
    ubicacion = models.CharField('Ubicación', max_length=200, blank=True)
    fecha_inicio = models.DateField('Fecha inicio')
    fecha_fin = models.DateField('Fecha fin', null=True, blank=True)
    en_curso = models.BooleanField('En curso', default=False)
    orden = models.PositiveSmallIntegerField('Orden', default=0)

    class Meta:
        verbose_name = 'Formación académica'
        verbose_name_plural = 'Formaciones académicas'
        ordering = ['orden', '-fecha_inicio']

    def __str__(self):
        return f'{self.titulo} – {self.centro}'

    @property
    def periodo(self):
        fin = 'En curso' if self.en_curso else (self.fecha_fin.strftime('%m/%Y') if self.fecha_fin else '')
        return f'{self.fecha_inicio.strftime("%m/%Y")} – {fin}'


# ─── Section 5: Complementary training ───────────────────────────────────────

TIPO_FORMACION_CHOICES = [
    ('curso', 'Curso'),
    ('certificacion', 'Certificación'),
    ('bootcamp', 'Bootcamp'),
    ('taller', 'Taller'),
    ('otro', 'Otro'),
]


class ComplementaryTraining(models.Model):
    cv = models.ForeignKey(
        CurriculumVitae, on_delete=models.CASCADE, related_name='trainings',
    )
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_FORMACION_CHOICES, default='curso')
    nombre = models.CharField('Nombre', max_length=200)
    entidad = models.CharField('Entidad / Institución', max_length=200, blank=True)
    fecha = models.DateField('Fecha', null=True, blank=True)
    descripcion = models.CharField('Descripción breve', max_length=300, blank=True)
    orden = models.PositiveSmallIntegerField('Orden', default=0)

    class Meta:
        verbose_name = 'Formación complementaria'
        verbose_name_plural = 'Formaciones complementarias'
        ordering = ['orden', '-fecha']

    def __str__(self):
        return f'{self.get_tipo_display()}: {self.nombre}'


# ─── Section 6: Skills ────────────────────────────────────────────────────────

TIPO_SKILL_CHOICES = [
    ('hard', 'Hard Skill (técnica)'),
    ('soft', 'Soft Skill (blanda)'),
]

CATEGORIA_SKILL_CHOICES = [
    ('lenguaje', 'Lenguaje de programación'),
    ('framework', 'Framework / Librería'),
    ('herramienta', 'Herramienta'),
    ('otro', 'Otro'),
    ('', 'Sin categoría'),
]


class Skill(models.Model):
    cv = models.ForeignKey(
        CurriculumVitae, on_delete=models.CASCADE, related_name='skills',
    )
    tipo = models.CharField('Tipo', max_length=10, choices=TIPO_SKILL_CHOICES, default='hard')
    categoria = models.CharField('Categoría', max_length=20, choices=CATEGORIA_SKILL_CHOICES, blank=True)
    nombre = models.CharField('Habilidad', max_length=100)
    nivel = models.PositiveSmallIntegerField(
        'Nivel (1–5)', null=True, blank=True,
        help_text='1=Básico, 5=Experto',
    )
    orden = models.PositiveSmallIntegerField('Orden', default=0)

    class Meta:
        verbose_name = 'Habilidad'
        verbose_name_plural = 'Habilidades'
        ordering = ['tipo', 'orden', 'nombre']

    def __str__(self):
        return self.nombre


# ─── Section 7: Languages ─────────────────────────────────────────────────────

NIVEL_IDIOMA_CHOICES = [
    ('nativo', 'Nativo'),
    ('C2', 'C2 – Maestría'),
    ('C1', 'C1 – Dominio operativo eficaz'),
    ('B2', 'B2 – Avanzado'),
    ('B1', 'B1 – Intermedio'),
    ('A2', 'A2 – Básico'),
    ('A1', 'A1 – Principiante'),
]


class Language(models.Model):
    cv = models.ForeignKey(
        CurriculumVitae, on_delete=models.CASCADE, related_name='languages',
    )
    idioma = models.CharField('Idioma', max_length=100)
    nivel = models.CharField('Nivel', max_length=10, choices=NIVEL_IDIOMA_CHOICES)
    certificacion = models.CharField('Certificación', max_length=200, blank=True)
    orden = models.PositiveSmallIntegerField('Orden', default=0)

    class Meta:
        verbose_name = 'Idioma'
        verbose_name_plural = 'Idiomas'
        ordering = ['orden']

    def __str__(self):
        return f'{self.idioma} – {self.get_nivel_display()}'


# ─── Section 8: Projects ──────────────────────────────────────────────────────

class Project(models.Model):
    cv = models.ForeignKey(
        CurriculumVitae, on_delete=models.CASCADE, related_name='projects',
    )
    nombre = models.CharField('Nombre del proyecto', max_length=200)
    descripcion = models.TextField('Descripción', blank=True)
    tecnologias = models.CharField('Tecnologías usadas', max_length=300, blank=True)
    link = models.URLField('Enlace (GitHub / web)', blank=True)
    orden = models.PositiveSmallIntegerField('Orden', default=0)

    class Meta:
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'
        ordering = ['orden']

    def __str__(self):
        return self.nombre


# ─── Section 9: Achievements ──────────────────────────────────────────────────

TIPO_LOGRO_CHOICES = [
    ('premio', 'Premio'),
    ('merito', 'Mérito académico'),
    ('evento', 'Participación en evento'),
    ('otro', 'Otro'),
]


class Achievement(models.Model):
    cv = models.ForeignKey(
        CurriculumVitae, on_delete=models.CASCADE, related_name='achievements',
    )
    titulo = models.CharField('Título / Descripción', max_length=200)
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_LOGRO_CHOICES, default='otro')
    descripcion = models.TextField('Detalle', blank=True)
    fecha = models.DateField('Fecha', null=True, blank=True)
    orden = models.PositiveSmallIntegerField('Orden', default=0)

    class Meta:
        verbose_name = 'Logro / Reconocimiento'
        verbose_name_plural = 'Logros y reconocimientos'
        ordering = ['orden', '-fecha']

    def __str__(self):
        return self.titulo


# ─── Section 10: Volunteering ────────────────────────────────────────────────

class Volunteering(models.Model):
    cv = models.ForeignKey(
        CurriculumVitae, on_delete=models.CASCADE, related_name='volunteerings',
    )
    organizacion = models.CharField('Organización', max_length=200)
    funcion = models.CharField('Función / Rol', max_length=200)
    impacto = models.TextField('Impacto', blank=True)
    fecha_inicio = models.DateField('Fecha inicio', null=True, blank=True)
    fecha_fin = models.DateField('Fecha fin', null=True, blank=True)
    en_curso = models.BooleanField('En curso', default=False)
    orden = models.PositiveSmallIntegerField('Orden', default=0)

    class Meta:
        verbose_name = 'Voluntariado'
        verbose_name_plural = 'Voluntariados'
        ordering = ['orden']

    def __str__(self):
        return f'{self.funcion} en {self.organizacion}'


# ─── Section 11: Social networks ─────────────────────────────────────────────

class SocialNetwork(models.Model):
    cv = models.OneToOneField(
        CurriculumVitae, on_delete=models.CASCADE, related_name='social_networks',
    )
    linkedin = models.URLField('LinkedIn', blank=True)
    github = models.URLField('GitHub', blank=True)
    portfolio = models.URLField('Portfolio / Web personal', blank=True)
    twitter = models.URLField('Twitter / X', blank=True)
    otras = models.CharField('Otras redes (describe)', max_length=500, blank=True)

    class Meta:
        verbose_name = 'Redes profesionales'

    def __str__(self):
        return f'Redes de {self.cv}'


# ─── Section 12: Interests ────────────────────────────────────────────────────

class Interest(models.Model):
    cv = models.ForeignKey(
        CurriculumVitae, on_delete=models.CASCADE, related_name='interests',
    )
    nombre = models.CharField('Interés', max_length=100)
    orden = models.PositiveSmallIntegerField('Orden', default=0)

    class Meta:
        verbose_name = 'Interés'
        verbose_name_plural = 'Intereses'
        ordering = ['orden']

    def __str__(self):
        return self.nombre


# ─── Section 13: Other info ───────────────────────────────────────────────────

TELETRABAJO_CHOICES = [
    ('si', 'Sí, 100% remoto'),
    ('parcial', 'Teletrabajo parcial'),
    ('no', 'Presencial'),
    ('indiferente', 'Indiferente'),
]


class OtherInfo(models.Model):
    cv = models.OneToOneField(
        CurriculumVitae, on_delete=models.CASCADE, related_name='other_info',
    )
    disponibilidad_viajar = models.BooleanField('Disponibilidad para viajar', default=False)
    teletrabajo = models.CharField(
        'Disponibilidad de teletrabajo', max_length=20,
        choices=TELETRABAJO_CHOICES, default='indiferente',
    )
    expectativa_salarial = models.CharField('Expectativas salariales', max_length=200, blank=True)
    notas = models.TextField('Notas adicionales', blank=True)

    class Meta:
        verbose_name = 'Otros datos'


# ─── CV Profile ───────────────────────────────────────────────────────────────

TEMPLATE_CHOICES = [
    ('minimalist', 'Minimalista'),
    ('tech', 'Tech (VSCode style)'),
    ('normal', 'Clásico'),
]


class CVProfile(models.Model):
    """A curated subset of the master CV, published at a unique URL."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cv_profiles',
    )
    cv = models.ForeignKey(
        CurriculumVitae, on_delete=models.CASCADE, related_name='profiles',
    )
    nombre = models.CharField('Nombre del perfil', max_length=200,
                              help_text='Ej: "Desarrollador Frontend", "Data Analyst"')
    slug = models.SlugField(
        'URL slug', max_length=100,
        help_text='Ej: OscarBurgos_frontend → opentowork.es/OscarBurgos_frontend',
    )
    template = models.CharField('Plantilla', max_length=20, choices=TEMPLATE_CHOICES, default='minimalist')
    is_public = models.BooleanField('Perfil público', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Section visibility flags
    mostrar_perfil_profesional = models.BooleanField('Mostrar perfil profesional', default=True)
    mostrar_redes = models.BooleanField('Mostrar redes sociales', default=True)
    mostrar_intereses = models.BooleanField('Mostrar intereses', default=True)
    mostrar_otros = models.BooleanField('Mostrar otros datos', default=False)
    mostrar_voluntariado = models.BooleanField('Mostrar voluntariado', default=True)
    mostrar_logros = models.BooleanField('Mostrar logros', default=True)

    # Selected M2M items
    experiencias = models.ManyToManyField(WorkExperience, blank=True, verbose_name='Experiencias',
                                          related_name='profiles')
    educaciones = models.ManyToManyField(Education, blank=True, verbose_name='Formación académica',
                                         related_name='profiles')
    formaciones = models.ManyToManyField(ComplementaryTraining, blank=True,
                                         verbose_name='Formación complementaria', related_name='profiles')
    habilidades = models.ManyToManyField(Skill, blank=True, verbose_name='Habilidades', related_name='profiles')
    idiomas = models.ManyToManyField(Language, blank=True, verbose_name='Idiomas', related_name='profiles')
    proyectos = models.ManyToManyField(Project, blank=True, verbose_name='Proyectos', related_name='profiles')
    logros = models.ManyToManyField(Achievement, blank=True, verbose_name='Logros', related_name='profiles')
    voluntariados = models.ManyToManyField(Volunteering, blank=True, verbose_name='Voluntariados',
                                           related_name='profiles')
    intereses = models.ManyToManyField(Interest, blank=True, verbose_name='Intereses', related_name='profiles')

    class Meta:
        verbose_name = 'Perfil de CV'
        verbose_name_plural = 'Perfiles de CV'
        unique_together = [['user', 'slug']]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.nombre} ({self.slug})'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('curriculum_public_cv', kwargs={'slug': self.slug})
