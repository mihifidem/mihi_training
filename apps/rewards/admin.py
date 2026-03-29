from django.contrib import admin
from .models import Recompensa, CanjeRecompensa


@admin.register(Recompensa)
class RecompensaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'puntos_necesarios', 'stock', 'activa')
    list_filter = ('activa',)
    search_fields = ('nombre',)
    list_editable = ('activa', 'stock')


@admin.register(CanjeRecompensa)
class CanjeAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'recompensa', 'puntos_gastados', 'estado', 'fecha_canje')
    list_filter = ('estado',)
    search_fields = ('usuario__username', 'recompensa__nombre')
    list_editable = ('estado',)
    date_hierarchy = 'fecha_canje'
