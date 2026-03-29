from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('admin/', views.DashboardAdminView.as_view(), name='dashboard_admin'),
    path('mi-progreso/', views.ProgresoAlumnoView.as_view(), name='mi_progreso'),
]
