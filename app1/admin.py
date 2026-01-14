from django.contrib import admin
from django.contrib import admin
from .models import Libro
@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'publicacion', 'disponible')
    search_fields = ('titulo', 'autor', 'publicacion', 'disponible')
# Register your models here.
