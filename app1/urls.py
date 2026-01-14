from django.urls import path
from app1 import views

urlpatterns = [
    path('', views.lista_libros, name='lista_libros'),
    path('nuevo/', views.crear_libro, name='crear_libro'),
    path('editar/<int:id>/', views.editar_libro, name='editar_libro'),
    path('eliminar/<int:id>/', views.eliminar_libro, name='eliminar_libro'),
    path('generar-pdf/', views.generar_pdf, name='generar_pdf'),
    path('prestar/<int:id>/', views.prestar_libro, name='prestar_libro'),
    path('regresar/<int:id>/', views.regresar_libro, name='regresar_libro'),

]