"""Forms for the users app."""
from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Aula, User


CODIGO_ACCESO_ALUMNO = '010819'


class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Correo electrónico')
    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellidos')
    codigo_acceso = forms.CharField(
        required=True,
        label='Código de acceso',
        help_text='Introduce el código que te haya facilitado el centro.',
    )
    aula = forms.ModelChoiceField(
        queryset=Aula.objects.order_by('nombre'),
        required=False,
        label='Aula',
        empty_label='Selecciona un aula',
    )

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'codigo_acceso', 'aula', 'password1', 'password2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            css = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            field.widget.attrs['class'] = css
        self.fields['aula'].widget.attrs['disabled'] = 'disabled'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        codigo_acceso = (self.cleaned_data.get('codigo_acceso') or '').strip()

        if codigo_acceso == CODIGO_ACCESO_ALUMNO:
            user.role = 'alumno'
            user.aula = self.cleaned_data.get('aula')
        else:
            user.role = 'basic'
            user.aula = None

        if commit:
            user.save()
        return user


class PerfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'bio', 'avatar', 'fecha_nacimiento', 'aula')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'aula': forms.Select(attrs={'class': 'form-select'}),
        }
