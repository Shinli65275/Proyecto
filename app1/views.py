from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Libro
from .forms import LibroForm
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def lista_libros(request):
    libros = Libro.objects.all()
    return render(request, 'lista.html', {'libros':libros})

def crear_libro(request):
    form = LibroForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('lista_libros')
    return render(request, 'form.html', {'form': form})

def editar_libro(request, id):
    libro = get_object_or_404(Libro, id=id)
    form = LibroForm(request.POST or None, instance=libro)
    if form.is_valid():
        form.save()
        return redirect('lista_libros')
    return render(request, 'editar.html', {'form': form})

def eliminar_libro(request, id):
    libro = get_object_or_404(Libro, id=id)
    if request.method == 'POST':
        libro.delete()
        return redirect('lista_libros')
    return render(request, 'eliminar.html', {'libro': libro})

def generar_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="lista_libros.pdf"'
    p = canvas.Canvas(response, pagesize=letter)
    p.setFont("Helvetica", 12)
    p.drawString(100, 750, "Lista de libros")
    libros = Libro.objects.all()
    y = 720 # posición inicial
    for libros in libros:
        texto = f"{libros.titulo} {libros.autor} {libros.publicacion}- {libros.disponible}"
        p.drawString(80, y, texto)
        y -= 20 # Espaciado entre líneas
        # Crear nueva página si se llena
        if y < 50:
            p.showPage()
            p.setFont("Helvetica", 12)
            y = 750
    p.showPage()
    p.save()
    return response
# Create your views here.

def prestar_libro(request, id):
    libro = get_object_or_404(Libro, id=id)
    if request.method == 'POST':
        libro.disponible = False
        libro.save()
        return redirect('lista_libros')
    return render(request, 'prestamo.html', {'libro': libro})

def regresar_libro(request, id):
    libro = get_object_or_404(Libro, id=id)
    if request.method == 'POST':
        libro.disponible = True
        libro.save()
        return redirect('lista_libros')
    return render(request, 'regreso.html', {'libro': libro})