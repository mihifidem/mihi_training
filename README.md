# MihiTraining — Plataforma Educativa SaaS

Plataforma web educativa completa con gamificación, cursos, certificados, IA tutor y marketplace de recompensas.

## Stack

- **Backend:** Django 4.2 + Django REST Framework
- **Auth:** django-allauth (usuario/contraseña + Google OAuth)
- **BD:** SQLite (dev) / PostgreSQL (prod)
- **Cache/Queue:** Redis + Celery
- **PDF:** ReportLab
- **IA:** OpenAI GPT-4o
- **Frontend:** Bootstrap 5

## Estructura de Apps

| App | Responsabilidad |
|-----|----------------|
| `users` | Modelo de usuario personalizado, perfiles, notificaciones |
| `courses` | Cursos, temas, inscripciones, progreso, quizzes |
| `gamification` | Insignias, logros, misiones, streaks, niveles |
| `rewards` | Marketplace, recompensas, historial de canjes |
| `analytics` | Dashboard, actividad, rutas de aprendizaje |
| `certifications` | Certificados con generación de PDF y validación |
| `ai_tutor` | Chatbot tutor con historial de conversación |
| `api` | Router DRF unificado + docs Swagger |

## Instalación

```bash
# 1. Clonar y crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
copy .env.example .env
# Editar .env con tus valores

# 4. Migraciones
python manage.py migrate

# 5. Crear superusuario
python manage.py createsuperuser

# 6. Cargar datos iniciales (insignias, misiones, etc.)
python manage.py loaddata fixtures/initial_data.json

# 7. Lanzar servidor de desarrollo
python manage.py runserver
```

## Ejecutar Celery (tareas asíncronas)

```bash
# Worker
celery -A config worker -l info

# Beat scheduler (tareas periódicas)
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## API Docs

Con el servidor corriendo, visita:
- Swagger UI: http://localhost:8000/api/v1/docs/
- ReDoc: http://localhost:8000/api/v1/redoc/

## Variables de Entorno

Ver `.env.example` para la lista completa de variables requeridas.
