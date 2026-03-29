"""Models for the rewards/marketplace app."""
from django.db import models
from django.conf import settings


class Recompensa(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='recompensas/', null=True, blank=True)
    puntos_necesarios = models.PositiveIntegerField()
    stock = models.IntegerField(default=-1, help_text='-1 = stock ilimitado')
    activa = models.BooleanField(default=True)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Recompensa'
        verbose_name_plural = 'Recompensas'
        ordering = ['puntos_necesarios']

    def __str__(self):
        return self.nombre

    @property
    def disponible(self):
        return self.activa and (self.stock == -1 or self.stock > 0)


class CanjeRecompensa(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesado', 'Procesado'),
        ('rechazado', 'Rechazado'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='canjes'
    )
    recompensa = models.ForeignKey(Recompensa, on_delete=models.CASCADE, related_name='canjes')
    fecha_canje = models.DateTimeField(auto_now_add=True)
    puntos_gastados = models.PositiveIntegerField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    notas_admin = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Canje'
        verbose_name_plural = 'Canjes'
        ordering = ['-fecha_canje']

    def __str__(self):
        return f'{self.usuario.username} → {self.recompensa.nombre} ({self.estado})'
