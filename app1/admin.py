from django.contrib import admin
from .models import Libro, Prestamo, Multa, HistorialMovimiento, ConfiguracionSistema

@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'autor', 'codigo_inventario', 'categoria', 'disponible']
    list_filter = ['categoria', 'disponible', 'condicion', 'idioma']
    search_fields = ['titulo', 'autor', 'codigo_inventario']
    list_per_page = 20
    ordering = ['-creado_en']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'subtitulo', 'autor', 'editorial')
        }),
        ('Detalles de Publicación', {
            'fields': ('publicacion', 'edicion', 'num_paginas', 'idioma')
        }),
        ('Clasificación', {
            'fields': ('categoria', 'condicion')
        }),
        ('Inventario', {
            'fields': ('codigo_inventario', 'precio_adquisicion', 'disponible')
        }),
        ('Información Adicional', {
            'fields': ('descripcion', 'portada'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ['libro', 'alumno_nombre', 'alumno_matricula', 'fecha_prestamo', 'fecha_vencimiento', 'estado', 'activo']
    list_filter = ['estado', 'activo', 'fecha_prestamo', 'fecha_vencimiento']
    search_fields = ['alumno_nombre', 'alumno_matricula', 'libro__titulo']
    date_hierarchy = 'fecha_prestamo'
    list_per_page = 20
    
    fieldsets = (
        ('Libro', {
            'fields': ('libro',)
        }),
        ('Información del Alumno', {
            'fields': ('alumno_nombre', 'alumno_matricula', 'alumno_grado', 'alumno_grupo', 'alumno_telefono')
        }),
        ('Fechas', {
            'fields': ('fecha_prestamo', 'fecha_vencimiento', 'fecha_devolucion_real')
        }),
        ('Estado', {
            'fields': ('activo', 'estado', 'renovaciones')
        }),
        ('Notas', {
            'fields': ('notas_prestamo', 'notas_devolucion')
        }),
        ('Multas', {
            'fields': ('tiene_multa', 'monto_multa', 'multa_pagada')
        }),
        ('Responsables', {
            'fields': ('prestado_por', 'recibido_por')
        }),
    )


@admin.register(Multa)
class MultaAdmin(admin.ModelAdmin):
    list_display = ['id', 'alumno_nombre', 'tipo', 'monto', 'estado', 'fecha_multa']
    list_filter = ['tipo', 'estado', 'fecha_multa']
    search_fields = ['alumno_nombre', 'alumno_matricula', 'descripcion']
    date_hierarchy = 'fecha_multa'
    list_per_page = 20


@admin.register(HistorialMovimiento)
class HistorialMovimientoAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'fecha', 'libro', 'alumno_nombre', 'usuario_responsable']
    list_filter = ['tipo', 'fecha']
    search_fields = ['descripcion', 'alumno_nombre', 'usuario_responsable']
    date_hierarchy = 'fecha'
    list_per_page = 30
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ConfiguracionSistema)
class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Configuración de Préstamos', {
            'fields': ('dias_prestamo', 'max_renovaciones', 'max_prestamos_simultaneos')
        }),
        ('Configuración de Multas', {
            'fields': ('multa_por_dia', 'dias_gracia')
        }),
        ('Información de la Biblioteca', {
            'fields': ('nombre_biblioteca', 'direccion', 'telefono', 'email', 'horario')
        }),
    )
    
    def has_add_permission(self, request):
        return not ConfiguracionSistema.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False