"""Forms for the Curriculum Vitae builder app."""
from django import forms
from django.forms import inlineformset_factory
from .models import (
    CurriculumVitae, PersonalInfo, ProfessionalProfile, WorkExperience,
    Education, ComplementaryTraining, Skill, Language, Project, Achievement,
    Volunteering, SocialNetwork, Interest, OtherInfo, CVProfile,
)

_DATE_WIDGET = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
_TEXT_WIDGET = forms.Textarea(attrs={'class': 'form-control', 'rows': 3})


def _fc(widget_class='form-control', **kwargs):
    return {'class': widget_class, **kwargs}


class PersonalInfoForm(forms.ModelForm):
    class Meta:
        model = PersonalInfo
        exclude = ['cv']
        widgets = {
            'nombre': forms.TextInput(attrs=_fc()),
            'apellidos': forms.TextInput(attrs=_fc()),
            'telefono1': forms.TextInput(attrs=_fc()),
            'telefono2': forms.TextInput(attrs=_fc()),
            'email_profesional1': forms.EmailInput(attrs=_fc()),
            'email_profesional2': forms.EmailInput(attrs=_fc()),
            'ciudad': forms.TextInput(attrs=_fc()),
            'pais': forms.TextInput(attrs=_fc()),
            'codigo_postal': forms.TextInput(attrs=_fc()),
            'fecha_nacimiento': _DATE_WIDGET,
            'nacionalidad': forms.TextInput(attrs=_fc()),
            'carnet_conducir': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'disponibilidad': forms.Select(attrs=_fc()),
            'foto': forms.ClearableFileInput(attrs=_fc()),
        }


class ProfessionalProfileForm(forms.ModelForm):
    class Meta:
        model = ProfessionalProfile
        exclude = ['cv']
        widgets = {
            'profesion': forms.TextInput(attrs=_fc()),
            'objetivo': forms.TextInput(attrs=_fc()),
            'resumen': forms.Textarea(attrs={**_fc(), 'rows': 5}),
        }


class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        exclude = ['cv', 'orden']
        widgets = {
            'puesto': forms.TextInput(attrs=_fc()),
            'empresa': forms.TextInput(attrs=_fc()),
            'ubicacion': forms.TextInput(attrs=_fc()),
            'fecha_inicio': _DATE_WIDGET,
            'fecha_fin': _DATE_WIDGET,
            'trabajo_actual': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'descripcion': forms.Textarea(attrs={**_fc(), 'rows': 4}),
            'logros': forms.Textarea(attrs={**_fc(), 'rows': 3,
                                           'placeholder': 'Un logro por línea…'}),
        }

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('trabajo_actual') and not cleaned.get('fecha_fin'):
            # fecha_fin is optional (might still be current job without checking the box)
            pass
        return cleaned


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        exclude = ['cv', 'orden']
        widgets = {
            'titulo': forms.TextInput(attrs=_fc()),
            'centro': forms.TextInput(attrs=_fc()),
            'ubicacion': forms.TextInput(attrs=_fc()),
            'fecha_inicio': _DATE_WIDGET,
            'fecha_fin': _DATE_WIDGET,
            'en_curso': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ComplementaryTrainingForm(forms.ModelForm):
    class Meta:
        model = ComplementaryTraining
        exclude = ['cv', 'orden']
        widgets = {
            'tipo': forms.Select(attrs=_fc()),
            'nombre': forms.TextInput(attrs=_fc()),
            'entidad': forms.TextInput(attrs=_fc()),
            'fecha': _DATE_WIDGET,
            'descripcion': forms.TextInput(attrs=_fc()),
        }


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        exclude = ['cv', 'orden']
        widgets = {
            'tipo': forms.Select(attrs=_fc()),
            'categoria': forms.Select(attrs=_fc()),
            'nombre': forms.TextInput(attrs=_fc()),
            'nivel': forms.NumberInput(attrs={**_fc(), 'min': 1, 'max': 5}),
        }


class LanguageForm(forms.ModelForm):
    class Meta:
        model = Language
        exclude = ['cv', 'orden']
        widgets = {
            'idioma': forms.TextInput(attrs=_fc()),
            'nivel': forms.Select(attrs=_fc()),
            'certificacion': forms.TextInput(attrs=_fc()),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ['cv', 'orden']
        widgets = {
            'nombre': forms.TextInput(attrs=_fc()),
            'descripcion': forms.Textarea(attrs={**_fc(), 'rows': 3}),
            'tecnologias': forms.TextInput(attrs=_fc()),
            'link': forms.URLInput(attrs=_fc()),
        }


class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        exclude = ['cv', 'orden']
        widgets = {
            'titulo': forms.TextInput(attrs=_fc()),
            'tipo': forms.Select(attrs=_fc()),
            'descripcion': forms.Textarea(attrs={**_fc(), 'rows': 3}),
            'fecha': _DATE_WIDGET,
        }


class VolunteeringForm(forms.ModelForm):
    class Meta:
        model = Volunteering
        exclude = ['cv', 'orden']
        widgets = {
            'organizacion': forms.TextInput(attrs=_fc()),
            'funcion': forms.TextInput(attrs=_fc()),
            'impacto': forms.Textarea(attrs={**_fc(), 'rows': 3}),
            'fecha_inicio': _DATE_WIDGET,
            'fecha_fin': _DATE_WIDGET,
            'en_curso': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SocialNetworkForm(forms.ModelForm):
    class Meta:
        model = SocialNetwork
        exclude = ['cv']
        widgets = {
            'linkedin': forms.URLInput(attrs={**_fc(), 'placeholder': 'https://linkedin.com/in/…'}),
            'github': forms.URLInput(attrs={**_fc(), 'placeholder': 'https://github.com/…'}),
            'portfolio': forms.URLInput(attrs={**_fc(), 'placeholder': 'https://miportfolio.com'}),
            'twitter': forms.URLInput(attrs={**_fc(), 'placeholder': 'https://twitter.com/…'}),
            'otras': forms.TextInput(attrs=_fc()),
        }


class InterestForm(forms.ModelForm):
    class Meta:
        model = Interest
        exclude = ['cv', 'orden']
        widgets = {
            'nombre': forms.TextInput(attrs=_fc()),
        }


class OtherInfoForm(forms.ModelForm):
    class Meta:
        model = OtherInfo
        exclude = ['cv']
        widgets = {
            'disponibilidad_viajar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'teletrabajo': forms.Select(attrs=_fc()),
            'expectativa_salarial': forms.TextInput(attrs=_fc()),
            'notas': forms.Textarea(attrs={**_fc(), 'rows': 3}),
        }


class CVProfileForm(forms.ModelForm):
    class Meta:
        model = CVProfile
        exclude = ['user', 'cv', 'created_at',
                   'experiencias', 'educaciones', 'formaciones',
                   'habilidades', 'idiomas', 'proyectos', 'logros',
                   'voluntariados', 'intereses']
        widgets = {
            'nombre': forms.TextInput(attrs=_fc()),
            'slug': forms.TextInput(attrs={**_fc(),
                                          'placeholder': 'NombreApellido_perfil'}),
            'template': forms.Select(attrs=_fc()),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mostrar_perfil_profesional': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mostrar_redes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mostrar_intereses': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mostrar_otros': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mostrar_voluntariado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mostrar_logros': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
