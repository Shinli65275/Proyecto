from django import forms
from .models import Libro, Prestamo, Multa

class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = [
            'isbn', 'titulo', 'subtitulo', 'autor', 'editorial', 
            'publicacion', 'edicion', 'categoria', 'num_paginas', 
            'idioma', 'ubicacion', 'codigo_inventario', 'condicion',
            'precio_adquisicion', 'descripcion', 'portada'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del libro'
            }),
            'subtitulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subtítulo (opcional)'
            }),
            'autor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del autor'
            }),
            'editorial': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Editorial'
            }),
            'publicacion': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Año de publicación',
                'min': '1000',
                'max': '9999'
            }),
            'edicion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: 1ra, 2da, 3ra'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-control'
            }),
            'num_paginas': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de páginas'
            }),
            'idioma': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Idioma'
            }),
            'codigo_inventario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código único de inventario'
            }),
            'condicion': forms.Select(attrs={
                'class': 'form-control'
            }),
            'precio_adquisicion': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción o sinopsis del libro'
            }),
            'portada': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        labels = {
            'isbn': 'ISBN',
            'titulo': 'Título',
            'subtitulo': 'Subtítulo',
            'autor': 'Autor',
            'editorial': 'Editorial',
            'publicacion': 'Año de Publicación',
            'edicion': 'Edición',
            'categoria': 'Categoría',
            'num_paginas': 'Número de Páginas',
            'idioma': 'Idioma',
            'ubicacion': 'Ubicación en Biblioteca',
            'codigo_inventario': 'Código de Inventario',
            'condicion': 'Condición',
            'precio_adquisicion': 'Precio de Adquisición',
            'descripcion': 'Descripción',
            'portada': 'Portada',
        }


class PrestamoForm(forms.ModelForm):
    class Meta:
        model = Prestamo
        fields = [
            'libro', 'alumno_nombre', 'alumno_matricula', 
            'alumno_grado', 'alumno_grupo', 'alumno_telefono',
            'fecha_vencimiento', 'notas_prestamo'
        ]
        widgets = {
            'libro': forms.Select(attrs={
                'class': 'form-control'
            }),
            'alumno_nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del alumno'
            }),
            'alumno_matricula': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Matrícula del alumno'
            }),
            'alumno_grado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: 3ro'
            }),
            'alumno_grupo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: A'
            }),
            'alumno_telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono de contacto'
            }),
            'fecha_vencimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notas_prestamo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales (opcional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar solo libros disponibles
        self.fields['libro'].queryset = Libro.objects.filter(disponible=True)


class DevolucionForm(forms.Form):
    """Formulario para devolución de libros"""
    notas_devolucion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Observaciones sobre el estado del libro o la devolución (opcional)'
        }),
        label='Notas de Devolución'
    )


class MultaForm(forms.ModelForm):
    class Meta:
        model = Multa
        fields = [
            'prestamo', 'libro', 'alumno_nombre', 'alumno_matricula',
            'tipo', 'monto', 'descripcion'
        ]
        widgets = {
            'prestamo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'libro': forms.Select(attrs={
                'class': 'form-control'
            }),
            'alumno_nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del alumno'
            }),
            'alumno_matricula': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Matrícula del alumno'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'monto': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la multa'
            }),
        }
        labels = {
            'prestamo': 'Préstamo (opcional)',
            'libro': 'Libro (opcional)',
            'alumno_nombre': 'Nombre del Alumno',
            'alumno_matricula': 'Matrícula',
            'tipo': 'Tipo de Multa',
            'monto': 'Monto',
            'descripcion': 'Descripción',
        }