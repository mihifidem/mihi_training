"""
Signal handlers for the curriculum app.

Awards gamification points the FIRST time each CV section is completed:
  - For OneToOne sections (PersonalInfo, ProfessionalProfile, SocialNetwork,
    OtherInfo): fires on creation (created=True).
  - For FK sections (WorkExperience, Education, etc.): fires when the user
    saves their very first item in that section (count == 1 after save).
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import (
    PersonalInfo, ProfessionalProfile, SocialNetwork, OtherInfo,
    WorkExperience, Education, ComplementaryTraining, Skill, Language,
    Project, Achievement, Volunteering, Interest,
)

# Points awarded once per section
PUNTOS_POR_SECCION = {
    'datos_personales':       25,
    'perfil_profesional':     25,
    'redes_sociales':         15,
    'otros_datos':            10,
    'experiencia_laboral':    30,
    'educacion':              25,
    'formacion_complementaria': 20,
    'habilidades':            20,
    'idiomas':                20,
    'proyectos':              25,
    'logros':                 20,
    'voluntariado':           20,
    'intereses':              10,
}

NOMBRES_SECCION = {
    'datos_personales':         'Datos personales',
    'perfil_profesional':       'Perfil profesional',
    'redes_sociales':           'Redes profesionales',
    'otros_datos':              'Otros datos',
    'experiencia_laboral':      'Experiencia laboral',
    'educacion':                'Formación académica',
    'formacion_complementaria': 'Formación complementaria',
    'habilidades':              'Habilidades',
    'idiomas':                  'Idiomas',
    'proyectos':                'Proyectos',
    'logros':                   'Logros y reconocimientos',
    'voluntariado':             'Voluntariado',
    'intereses':                'Intereses',
}


def _award_cv_points(usuario, seccion_key):
    """Award points for a CV section. Idempotent – only fires once per section."""
    from apps.analytics.models import RegistroActividad

    # Guard: only award once (check by tipo + descripcion)
    descripcion = f'CV — {NOMBRES_SECCION[seccion_key]}'
    ya_otorgado = RegistroActividad.objects.filter(
        usuario=usuario,
        tipo='cv_seccion',
        descripcion=descripcion,
    ).exists()
    if ya_otorgado:
        return

    puntos = PUNTOS_POR_SECCION[seccion_key]

    # Award points via User helper (also updates level)
    usuario.agregar_puntos(puntos)

    # Log the activity
    RegistroActividad.objects.create(
        usuario=usuario,
        tipo='cv_seccion',
        descripcion=descripcion,
        puntos_ganados=puntos,
    )

    # Send in-app notification
    from apps.gamification.utils import crear_notificacion, verificar_insignias
    crear_notificacion(
        usuario,
        'logro',
        f'🎓 +{puntos} puntos',
        f'Completaste la sección «{NOMBRES_SECCION[seccion_key]}» de tu CV.',
    )

    # Check if any point/streak badge should now be awarded
    verificar_insignias(usuario)


# ── OneToOne sections ─────────────────────────────────────────────────────────

@receiver(post_save, sender=PersonalInfo)
def on_personal_info_saved(sender, instance, created, **kwargs):
    if created:
        _award_cv_points(instance.cv.user, 'datos_personales')


@receiver(post_save, sender=ProfessionalProfile)
def on_professional_profile_saved(sender, instance, created, **kwargs):
    if created:
        _award_cv_points(instance.cv.user, 'perfil_profesional')


@receiver(post_save, sender=SocialNetwork)
def on_social_network_saved(sender, instance, created, **kwargs):
    if created:
        _award_cv_points(instance.cv.user, 'redes_sociales')


@receiver(post_save, sender=OtherInfo)
def on_other_info_saved(sender, instance, created, **kwargs):
    if created:
        _award_cv_points(instance.cv.user, 'otros_datos')


# ── FK sections: award on first item ─────────────────────────────────────────

@receiver(post_save, sender=WorkExperience)
def on_work_experience_saved(sender, instance, created, **kwargs):
    if created and instance.cv.work_experiences.count() == 1:
        _award_cv_points(instance.cv.user, 'experiencia_laboral')


@receiver(post_save, sender=Education)
def on_education_saved(sender, instance, created, **kwargs):
    if created and instance.cv.educations.count() == 1:
        _award_cv_points(instance.cv.user, 'educacion')


@receiver(post_save, sender=ComplementaryTraining)
def on_training_saved(sender, instance, created, **kwargs):
    if created and instance.cv.trainings.count() == 1:
        _award_cv_points(instance.cv.user, 'formacion_complementaria')


@receiver(post_save, sender=Skill)
def on_skill_saved(sender, instance, created, **kwargs):
    if created and instance.cv.skills.count() == 1:
        _award_cv_points(instance.cv.user, 'habilidades')


@receiver(post_save, sender=Language)
def on_language_saved(sender, instance, created, **kwargs):
    if created and instance.cv.languages.count() == 1:
        _award_cv_points(instance.cv.user, 'idiomas')


@receiver(post_save, sender=Project)
def on_project_saved(sender, instance, created, **kwargs):
    if created and instance.cv.projects.count() == 1:
        _award_cv_points(instance.cv.user, 'proyectos')


@receiver(post_save, sender=Achievement)
def on_achievement_saved(sender, instance, created, **kwargs):
    if created and instance.cv.achievements.count() == 1:
        _award_cv_points(instance.cv.user, 'logros')


@receiver(post_save, sender=Volunteering)
def on_volunteering_saved(sender, instance, created, **kwargs):
    if created and instance.cv.volunteerings.count() == 1:
        _award_cv_points(instance.cv.user, 'voluntariado')


@receiver(post_save, sender=Interest)
def on_interest_saved(sender, instance, created, **kwargs):
    if created and instance.cv.interests.count() == 1:
        _award_cv_points(instance.cv.user, 'intereses')
