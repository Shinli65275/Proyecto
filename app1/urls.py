from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Libros
    path('libros/', views.lista_libros, name='lista_libros'),
    path('libros/crear/', views.crear_libro, name='crear_libro'),
    path('libros/<int:pk>/editar/', views.editar_libro, name='editar_libro'),
    path('libros/<int:pk>/eliminar/', views.eliminar_libro, name='eliminar_libro'),
    path('libros/disponibles/', views.libros_disponibles, name='libros_disponibles'),
    path('libros/prestados/', views.libros_prestados, name='libros_prestados'),
    
    # Préstamos
    path('prestamos/', views.lista_prestamos, name='lista_prestamos'),
    path('prestamos/crear/', views.crear_prestamo, name='crear_prestamo'),
    path('prestamos/<int:pk>/devolver/', views.devolver_prestamo, name='devolver_prestamo'),
    path('prestamos/<int:pk>/renovar/', views.renovar_prestamo, name='renovar_prestamo'),

    path('reporte/libros/pdf/', views.reporte_libros_pdf, name='reporte_libros_pdf'),
]