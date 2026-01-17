from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta, date
from .models import Libro, Prestamo, Multa, HistorialMovimiento, ConfiguracionSistema
from .forms import LibroForm, PrestamoForm, DevolucionForm, MultaForm
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors

from .models import Libro
from .models import ConfiguracionSistema

from django.utils import timezone


def home(request):
    """Vista principal del dashboard"""
    # Estadísticas generales
    total_libros = Libro.objects.count()
    libros_disponibles = Libro.objects.filter(disponible=True).count()
    prestamos_activos = Prestamo.objects.filter(activo=True).count()
    multas_pendientes = Multa.objects.filter(estado='pendiente').count()
    
    # Préstamos por vencer (próximos 3 días)
    from datetime import timedelta
    fecha_limite = timezone.now().date() + timedelta(days=3)
    prestamos_por_vencer = Prestamo.objects.filter(
        activo=True,
        fecha_vencimiento__lte=fecha_limite,
        fecha_vencimiento__gte=timezone.now().date()
    ).select_related('libro')[:5]
    
    # Últimos movimientos
    ultimos_movimientos = HistorialMovimiento.objects.all()[:10]
    
    # Estadísticas por categoría
    from django.db.models import Count
    stats_categorias = Libro.objects.values('categoria').annotate(total=Count('id'))
    categorias_dict = {stat['categoria']: stat['total'] for stat in stats_categorias}
    
    context = {
        'total_libros': total_libros,
        'libros_disponibles': libros_disponibles,
        'prestamos_activos': prestamos_activos,
        'multas_pendientes': multas_pendientes,
        'prestamos_por_vencer': prestamos_por_vencer,
        'ultimos_movimientos': ultimos_movimientos,
        'categorias_dict': categorias_dict,
    }
    return render(request, 'app1/home.html', context)


def lista_libros(request):
    """Vista para listar todos los libros con búsqueda y filtros"""
    libros = Libro.objects.all()
    
    # Búsqueda
    query = request.GET.get('q')
    if query:
        libros = libros.filter(
            Q(titulo__icontains=query) |
            Q(autor__icontains=query) |
            Q(codigo_inventario__icontains=query)
        )
    
    # Filtro por categoría
    categoria = request.GET.get('categoria')
    if categoria:
        libros = libros.filter(categoria=categoria)
    
    # Filtro por disponibilidad
    disponible = request.GET.get('disponible')
    if disponible:
        libros = libros.filter(disponible=disponible == 'true')
    
    categorias = Libro.CATEGORIAS
    
    context = {
        'libros': libros,
        'categorias': categorias,
        'query': query or '',
        'categoria_seleccionada': categoria or '',
    }
    return render(request, 'app1/lista_libros.html', context)


def crear_libro(request):
    """Vista para crear un nuevo libro"""
    if request.method == 'POST':
        form = LibroForm(request.POST, request.FILES)
        if form.is_valid():
            libro = form.save()
            
            # Registrar en historial
            HistorialMovimiento.objects.create(
                tipo='alta',
                libro=libro,
                descripcion=f'Alta de libro: {libro.titulo}',
                usuario_responsable=request.user.username if request.user.is_authenticated else 'Sistema'
            )
            
            messages.success(request, f'Libro "{libro.titulo}" agregado exitosamente.')
            return redirect('lista_libros')
    else:
        form = LibroForm()
    
    context = {
        'form': form,
        'titulo_pagina': 'Agregar Nuevo Libro'
    }
    return render(request, 'app1/crear_libro.html', context)


def editar_libro(request, pk):
    """Vista para editar un libro existente"""
    libro = get_object_or_404(Libro, pk=pk)
    
    if request.method == 'POST':
        form = LibroForm(request.POST, request.FILES, instance=libro)
        if form.is_valid():
            libro = form.save()
            
            # Registrar en historial
            HistorialMovimiento.objects.create(
                tipo='alta',
                libro=libro,
                descripcion=f'Actualización de libro: {libro.titulo}',
                usuario_responsable=request.user.username if request.user.is_authenticated else 'Sistema'
            )
            
            messages.success(request, f'Libro "{libro.titulo}" actualizado exitosamente.')
            return redirect('lista_libros')
    else:
        form = LibroForm(instance=libro)
    
    context = {
        'form': form,
        'libro': libro,
        'titulo_pagina': 'Editar Libro'
    }
    return render(request, 'app1/editar_libro.html', context)


def eliminar_libro(request, pk):
    """Vista para eliminar un libro"""
    libro = get_object_or_404(Libro, pk=pk)
    
    # Verificar si tiene préstamos activos
    if Prestamo.objects.filter(libro=libro, activo=True).exists():
        messages.error(request, 'No se puede eliminar un libro con préstamos activos.')
        return redirect('lista_libros')
    
    if request.method == 'POST':
        titulo = libro.titulo
        
        # Registrar en historial antes de eliminar
        HistorialMovimiento.objects.create(
            tipo='baja',
            descripcion=f'Baja de libro: {titulo} (ISBN: {libro.isbn})',
            usuario_responsable=request.user.username if request.user.is_authenticated else 'Sistema'
        )
        
        libro.delete()
        messages.success(request, f'Libro "{titulo}" eliminado exitosamente.')
        return redirect('lista_libros')
    
    context = {
        'libro': libro
    }
    return render(request, 'app1/eliminar_libro.html', context)


def libros_disponibles(request):
    """Vista para listar solo libros disponibles"""
    libros = Libro.objects.filter(disponible=True)
    
    # Búsqueda
    query = request.GET.get('q')
    if query:
        libros = libros.filter(
            Q(titulo__icontains=query) |
            Q(autor__icontains=query) |
            Q(isbn__icontains=query) |
            Q(codigo_inventario__icontains=query)
        )
    
    # Filtro por categoría
    categoria = request.GET.get('categoria')
    if categoria:
        libros = libros.filter(categoria=categoria)
    
    categorias = Libro.CATEGORIAS
    
    context = {
        'libros': libros,
        'categorias': categorias,
        'query': query or '',
        'categoria_seleccionada': categoria or '',
        'titulo_pagina': 'Libros Disponibles',
        'tipo_vista': 'disponibles'
    }
    return render(request, 'app1/libros_disponibles.html', context)


def libros_prestados(request):
    """Vista para listar solo libros prestados (no disponibles)"""
    from datetime import date
    libros = Libro.objects.filter(disponible=False).select_related()
    
    # Obtener información de préstamos activos
    libros_con_prestamo = []
    for libro in libros:
        prestamo_activo = Prestamo.objects.filter(libro=libro, activo=True).first()
        libros_con_prestamo.append({
            'libro': libro,
            'prestamo': prestamo_activo
        })
    
    # Búsqueda
    query = request.GET.get('q')
    if query:
        libros = libros.filter(
            Q(titulo__icontains=query) |
            Q(autor__icontains=query) |
            Q(isbn__icontains=query) |
            Q(codigo_inventario__icontains=query)
        )
    
    # Filtro por categoría
    categoria = request.GET.get('categoria')
    if categoria:
        libros = libros.filter(categoria=categoria)
    
    categorias = Libro.CATEGORIAS
    
    context = {
        'libros_con_prestamo': libros_con_prestamo,
        'categorias': categorias,
        'query': query or '',
        'categoria_seleccionada': categoria or '',
        'titulo_pagina': 'Libros Prestados',
        'tipo_vista': 'prestados',
        'today': date.today(),
    }
    return render(request, 'app1/libros_prestados.html', context)


# ==================== VISTAS DE PRÉSTAMOS ====================

def lista_prestamos(request):
    """Vista para listar todos los préstamos"""
    prestamos = Prestamo.objects.all().select_related('libro')
    
    # Filtros
    estado = request.GET.get('estado')
    if estado:
        prestamos = prestamos.filter(estado=estado)
    
    activo = request.GET.get('activo')
    if activo == 'true':
        prestamos = prestamos.filter(activo=True)
    elif activo == 'false':
        prestamos = prestamos.filter(activo=False)
    
    # Búsqueda
    query = request.GET.get('q')
    if query:
        prestamos = prestamos.filter(
            Q(alumno_nombre__icontains=query) |
            Q(alumno_matricula__icontains=query) |
            Q(libro__titulo__icontains=query)
        )
    
    # Préstamos vencidos
    prestamos_vencidos = prestamos.filter(
        activo=True,
        fecha_vencimiento__lt=timezone.now().date()
    ).count()
    
    context = {
        'prestamos': prestamos,
        'prestamos_vencidos': prestamos_vencidos,
        'query': query or '',
        'today': date.today(),
    }
    return render(request, 'app1/lista_prestamos.html', context)


def crear_prestamo(request):
    """Vista para crear un nuevo préstamo"""
    if request.method == 'POST':
        form = PrestamoForm(request.POST)
        if form.is_valid():
            prestamo = form.save(commit=False)
            
            # Verificar si el libro está disponible
            if not prestamo.libro.disponible:
                messages.error(request, 'Este libro no está disponible para préstamo.')
                return redirect('crear_prestamo')
            
            # Verificar límite de préstamos simultáneos
            config = ConfiguracionSistema.load()
            prestamos_activos = Prestamo.objects.filter(
                alumno_matricula=prestamo.alumno_matricula,
                activo=True
            ).count()
            
            if prestamos_activos >= config.max_prestamos_simultaneos:
                messages.error(
                    request, 
                    f'El alumno ya tiene {prestamos_activos} préstamos activos. '
                    f'Máximo permitido: {config.max_prestamos_simultaneos}'
                )
                return redirect('crear_prestamo')
            
            # Asignar usuario responsable
            prestamo.prestado_por = request.user.username if request.user.is_authenticated else 'Sistema'
            
            # Guardar préstamo
            prestamo.save()
            
            # Registrar en historial
            HistorialMovimiento.objects.create(
                tipo='prestamo',
                libro=prestamo.libro,
                prestamo=prestamo,
                alumno_nombre=prestamo.alumno_nombre,
                alumno_matricula=prestamo.alumno_matricula,
                descripcion=f'Préstamo de "{prestamo.libro.titulo}" a {prestamo.alumno_nombre}',
                usuario_responsable=request.user.username if request.user.is_authenticated else 'Sistema'
            )
            
            messages.success(
                request, 
                f'Préstamo registrado exitosamente. Fecha de devolución: {prestamo.fecha_vencimiento.strftime("%d/%m/%Y")}'
            )
            return redirect('lista_prestamos')
    else:
        form = PrestamoForm()
    
    # Obtener libros disponibles
    libros_disponibles = Libro.objects.filter(disponible=True).count()
    
    context = {
        'form': form,
        'libros_disponibles': libros_disponibles,
    }
    return render(request, 'app1/crear_prestamo.html', context)


def devolver_prestamo(request, pk):
    """Vista para devolver un libro prestado"""
    prestamo = get_object_or_404(Prestamo, pk=pk)
    
    if not prestamo.activo:
        messages.warning(request, 'Este préstamo ya fue devuelto.')
        return redirect('lista_prestamos')
    
    if request.method == 'POST':
        form = DevolucionForm(request.POST)
        if form.is_valid():
            # Actualizar préstamo
            prestamo.activo = False
            prestamo.estado = 'devuelto'
            prestamo.fecha_devolucion_real = timezone.now().date()
            prestamo.notas_devolucion = form.cleaned_data['notas_devolucion']
            prestamo.recibido_por = request.user.username if request.user.is_authenticated else 'Sistema'
            
            # Verificar si hay retraso y generar multa
            if prestamo.fecha_devolucion_real > prestamo.fecha_vencimiento:
                dias_retraso = (prestamo.fecha_devolucion_real - prestamo.fecha_vencimiento).days
                config = ConfiguracionSistema.load()
                
                if dias_retraso > config.dias_gracia:
                    dias_multa = dias_retraso - config.dias_gracia
                    monto_multa = dias_multa * config.multa_por_dia
                    
                    # Crear multa
                    multa = Multa.objects.create(
                        prestamo=prestamo,
                        libro=prestamo.libro,
                        alumno_nombre=prestamo.alumno_nombre,
                        alumno_matricula=prestamo.alumno_matricula,
                        tipo='retraso',
                        monto=monto_multa,
                        descripcion=f'Multa por {dias_multa} días de retraso en la devolución de "{prestamo.libro.titulo}"'
                    )
                    
                    prestamo.tiene_multa = True
                    prestamo.monto_multa = monto_multa
                    
                    messages.warning(
                        request,
                        f'Libro devuelto con {dias_retraso} días de retraso. '
                        f'Se generó una multa de ${monto_multa:.2f}'
                    )
            
            prestamo.save()
            
            # Registrar en historial
            HistorialMovimiento.objects.create(
                tipo='devolucion',
                libro=prestamo.libro,
                prestamo=prestamo,
                alumno_nombre=prestamo.alumno_nombre,
                alumno_matricula=prestamo.alumno_matricula,
                descripcion=f'Devolución de "{prestamo.libro.titulo}" por {prestamo.alumno_nombre}',
                usuario_responsable=request.user.username if request.user.is_authenticated else 'Sistema'
            )
            
            if not prestamo.tiene_multa:
                messages.success(request, 'Libro devuelto exitosamente.')
            
            return redirect('lista_prestamos')
    else:
        form = DevolucionForm()
    
    # Calcular días de retraso si los hay
    dias_retraso = 0
    if timezone.now().date() > prestamo.fecha_vencimiento:
        dias_retraso = (timezone.now().date() - prestamo.fecha_vencimiento).days
    
    context = {
        'prestamo': prestamo,
        'form': form,
        'dias_retraso': dias_retraso,
    }
    return render(request, 'app1/devolver_prestamo.html', context)


def renovar_prestamo(request, pk):
    """Vista para renovar un préstamo"""
    prestamo = get_object_or_404(Prestamo, pk=pk)
    config = ConfiguracionSistema.load()
    
    if not prestamo.activo:
        messages.error(request, 'No se puede renovar un préstamo que ya fue devuelto.')
        return redirect('lista_prestamos')
    
    if prestamo.renovaciones >= config.max_renovaciones:
        messages.error(
            request, 
            f'Este préstamo ya alcanzó el máximo de renovaciones ({config.max_renovaciones}).'
        )
        return redirect('lista_prestamos')
    
    # Verificar que no tenga multas pendientes
    if Multa.objects.filter(alumno_matricula=prestamo.alumno_matricula, estado='pendiente').exists():
        messages.error(request, 'El alumno tiene multas pendientes. Debe pagarlas antes de renovar.')
        return redirect('lista_prestamos')
    
    if request.method == 'POST':
        # Renovar préstamo
        prestamo.renovaciones += 1
        prestamo.fecha_vencimiento = timezone.now().date() + timedelta(days=config.dias_prestamo)
        prestamo.estado = 'renovado'
        prestamo.save()
        
        # Registrar en historial
        HistorialMovimiento.objects.create(
            tipo='renovacion',
            libro=prestamo.libro,
            prestamo=prestamo,
            alumno_nombre=prestamo.alumno_nombre,
            alumno_matricula=prestamo.alumno_matricula,
            descripcion=f'Renovación #{prestamo.renovaciones} de "{prestamo.libro.titulo}" para {prestamo.alumno_nombre}',
            usuario_responsable=request.user.username if request.user.is_authenticated else 'Sistema'
        )
        
        messages.success(
            request,
            f'Préstamo renovado exitosamente. Nueva fecha de vencimiento: {prestamo.fecha_vencimiento.strftime("%d/%m/%Y")}'
        )
        return redirect('lista_prestamos')
    
    context = {
        'prestamo': prestamo,
        'config': config,
    }
    return render(request, 'app1/renovar_prestamo.html', context)


# ==================== VISTAS DE MULTAS ====================

def lista_multas(request):
    """Vista para listar todas las multas"""
    multas = Multa.objects.all().select_related('libro', 'prestamo')
    
    # Filtros
    estado = request.GET.get('estado')
    if estado:
        multas = multas.filter(estado=estado)
    
    tipo = request.GET.get('tipo')
    if tipo:
        multas = multas.filter(tipo=tipo)
    
    # Búsqueda
    query = request.GET.get('q')
    if query:
        multas = multas.filter(
            Q(alumno_nombre__icontains=query) |
            Q(alumno_matricula__icontains=query) |
            Q(libro__titulo__icontains=query)
        )
    
    # Estadísticas
    multas_pendientes = multas.filter(estado='pendiente').count()
    total_pendiente = sum(m.monto for m in multas.filter(estado='pendiente'))
    
    context = {
        'multas': multas,
        'multas_pendientes': multas_pendientes,
        'total_pendiente': total_pendiente,
        'query': query or '',
    }
    return render(request, 'app1/lista_multas.html', context)


def crear_multa(request):
    """Vista para crear una multa manualmente"""
    if request.method == 'POST':
        form = MultaForm(request.POST)
        if form.is_valid():
            multa = form.save()
            
            messages.success(request, f'Multa de ${multa.monto:.2f} creada exitosamente.')
            return redirect('lista_multas')
    else:
        form = MultaForm()
    
    context = {
        'form': form,
    }
    return render(request, 'app1/crear_multa.html', context)


def pagar_multa(request, pk):
    """Vista para registrar el pago de una multa"""
    multa = get_object_or_404(Multa, pk=pk)
    
    if multa.estado == 'pagada':
        messages.warning(request, 'Esta multa ya fue pagada.')
        return redirect('lista_multas')
    
    if request.method == 'POST':
        recibo = request.POST.get('recibo', '')
        
        multa.estado = 'pagada'
        multa.fecha_pago = timezone.now().date()
        multa.recibo = recibo
        multa.save()
        
        # Actualizar préstamo si existe
        if multa.prestamo:
            multa.prestamo.multa_pagada = True
            multa.prestamo.save()
        
        messages.success(request, f'Multa de ${multa.monto:.2f} pagada exitosamente.')
        return redirect('lista_multas')
    
    context = {
        'multa': multa,
    }
    return render(request, 'app1/pagar_multa.html', context)


def condonar_multa(request, pk):
    """Vista para condonar una multa"""
    multa = get_object_or_404(Multa, pk=pk)
    
    if multa.estado != 'pendiente':
        messages.warning(request, 'Solo se pueden condonar multas pendientes.')
        return redirect('lista_multas')
    
    if request.method == 'POST':
        multa.estado = 'condonada'
        multa.save()
        
        messages.success(request, f'Multa de ${multa.monto:.2f} condonada exitosamente.')
        return redirect('lista_multas')
    
    context = {
        'multa': multa,
    }
    return render(request, 'app1/condonar_multa.html', context)

def reporte_libros_pdf(request):
    # Configuración de la respuesta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte_libros.pdf"'

    # Crear el PDF
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Cargar configuración del sistema
    config = ConfiguracionSistema.load()

    # Título
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width / 2, height - 2.5 * cm, config.nombre_biblioteca)

    p.setFont("Helvetica", 13)
    p.drawCentredString(width / 2, height - 3.5 * cm, "Reporte General de Libros")


    # Fecha
    p.setFont("Helvetica", 9)
    fecha_actual = timezone.now().strftime("%d/%m/%Y")
    p.drawRightString(
        width - 2 * cm,
        height - 1.5 * cm,
        f"Fecha de generación: {fecha_actual}"
    )


    # Espacio
    y = height - 4.5 * cm

    # Encabezados de tabla
    data = [
        [
            "Código",
            "Título",
            "Autor",
            "Categoría",
            "Año",
            "Disponible"
        ]
    ]

    # Obtener libros
    libros = Libro.objects.all()

    for libro in libros:
        data.append([
            libro.codigo_inventario,
            libro.titulo[:40],  # evitar textos muy largos
            libro.autor,
            libro.get_categoria_display(),
            libro.publicacion,
            "Sí" if libro.disponible else "No"
        ])

    # Crear tabla
    table = Table(data, colWidths=[3*cm, 5*cm, 4*cm, 3*cm, 2*cm, 2*cm])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (4, 1), (5, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))

    # Dibujar tabla
    table.wrapOn(p, width, height)
    table.drawOn(p, 2 * cm, height - 6 * cm)

    # Finalizar PDF
    p.showPage()
    p.save()

    return response
