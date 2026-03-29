from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

from apps.courses.models import Curso, InscripcionCurso, Progreso
from apps.gamification.models import Insignia
from apps.users.forms import RegistroForm
from apps.users.models import Aula
from apps.users.serializers import UserSerializer


class RegistroFormTests(TestCase):
    def setUp(self):
        self.aula = Aula.objects.create(
            nombre='Aula Registro',
            direccion='Calle Registro 10',
            horario='Manana',
        )

    def test_registro_asigna_role_basic_por_defecto(self):
        form = RegistroForm(data={
            'username': 'nuevo_usuario',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'email': 'nuevo@example.com',
            'codigo_acceso': 'xxxxxx',
            'password1': 'ClaveSegura123',
            'password2': 'ClaveSegura123',
        })

        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()

        self.assertEqual(user.role, 'basic')
        self.assertIsNone(user.aula)

    def test_registro_con_codigo_alumno_asigna_role_alumno_y_aula(self):
        form = RegistroForm(data={
            'username': 'alumno_nuevo',
            'first_name': 'Alumno',
            'last_name': 'Nuevo',
            'email': 'alumno@example.com',
            'codigo_acceso': '010819',
            'aula': self.aula.pk,
            'password1': 'ClaveSegura123',
            'password2': 'ClaveSegura123',
        })

        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()

        self.assertEqual(user.role, 'alumno')
        self.assertEqual(user.aula_id, self.aula.id)


class UserSerializerTests(TestCase):
    def test_serializer_expone_role(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(
            username='premium_user',
            password='test1234',
            role='premium',
        )

        serializer = UserSerializer(user)

        self.assertEqual(serializer.data['role'], 'premium')


@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class PerfilViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.aula = Aula.objects.create(
            nombre='Aula Perfil',
            direccion='Calle Perfil 1',
            horario='Tarde',
        )
        self.user = user_model.objects.create_user(
            username='alumno_demo',
            password='test1234',
            role='alumno',
            aula=self.aula,
        )
        self.client.force_login(self.user)

    def test_ficha_usuario_muestra_role(self):
        response = self.client.get(reverse('users:perfil', kwargs={'username': self.user.username}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Rol: Alumno')

    def test_ficha_usuario_muestra_insignia_de_tema_activa(self):
        curso = Curso.objects.create(
            nombre='Curso Perfil',
            descripcion='Descripcion',
            fecha_inicio=date.today(),
            horas_duracion=2,
            activo=True,
        )
        tema = curso.temas.create(
            titulo='Tema Perfil',
            contenido='Contenido',
            orden=1,
            puntos_otorgados=10,
        )
        insignia = Insignia.objects.create(
            nombre='Insignia Perfil',
            descripcion='Se activa al completar el tema',
            tipo='tema',
            tema_objetivo=tema,
            visible=True,
        )
        self.aula.cursos.add(curso)
        InscripcionCurso.objects.create(usuario=self.user, curso=curso)
        Progreso.objects.create(usuario=self.user, tema=tema, completado=True)

        response = self.client.get(reverse('users:perfil', kwargs={'username': self.user.username}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Insignias (1 / 1)')
        insignias_con_estado = dict(response.context['insignias_con_estado'])
        self.assertTrue(insignias_con_estado[insignia])