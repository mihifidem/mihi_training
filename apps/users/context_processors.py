"""Context processors for the users app."""
from .models import Notificacion


def notificaciones_no_leidas(request):
    """Inject unread notification count into every template context."""
    if request.user.is_authenticated:
        count = Notificacion.objects.filter(usuario=request.user, leida=False).count()
        return {'notificaciones_count': count}
    return {'notificaciones_count': 0}
