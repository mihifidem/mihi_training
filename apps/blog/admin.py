from django.contrib import admin

from .models import (
    CategoriaBlog,
    HashtagBlog,
    LecturaPostUsuario,
    PostBlog,
    SubcategoriaBlog,
    ValoracionPost,
)


@admin.register(CategoriaBlog)
class CategoriaBlogAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'activa')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('activa',)
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(SubcategoriaBlog)
class SubcategoriaBlogAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'slug', 'activa')
    search_fields = ('nombre', 'descripcion', 'categoria__nombre')
    list_filter = ('activa', 'categoria')
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(HashtagBlog)
class HashtagBlogAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug')
    search_fields = ('nombre',)
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(PostBlog)
class PostBlogAdmin(admin.ModelAdmin):
    list_display = (
        'titulo',
        'categoria',
        'subcategoria',
        'visibilidad',
        'publicado',
        'destacado',
        'publicado_en',
        'puntos_lectura',
    )
    list_filter = ('visibilidad', 'publicado', 'destacado', 'categoria', 'subcategoria')
    search_fields = ('titulo', 'resumen', 'contenido_publico', 'contenido_privado')
    prepopulated_fields = {'slug': ('titulo',)}
    filter_horizontal = ('hashtags',)
    date_hierarchy = 'publicado_en'


@admin.register(ValoracionPost)
class ValoracionPostAdmin(admin.ModelAdmin):
    list_display = ('post', 'usuario', 'valor', 'creada_en')
    list_filter = ('valor',)
    search_fields = ('post__titulo', 'usuario__username')
    date_hierarchy = 'creada_en'


@admin.register(LecturaPostUsuario)
class LecturaPostUsuarioAdmin(admin.ModelAdmin):
    list_display = ('post', 'usuario', 'iniciada_en', 'completada_en', 'puntos_otorgados')
    list_filter = ('puntos_otorgados',)
    search_fields = ('post__titulo', 'usuario__username')
    date_hierarchy = 'iniciada_en'
