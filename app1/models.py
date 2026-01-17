# app1/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta

class Libro(models.Model):
    CATEGORIAS = [
        ('ficcion', 'Ficción'),
        ('no_ficcion', 'No ficción'),
        ('ciencia', 'Ciencia'),
        ('tecnologia', 'Tecnología'),
        ('historia', 'Historia'),
        ('matematicas', 'Matemáticas'),
        ('literatura', 'Literatura'),
        ('referencia', 'Referencia'),
        ('arte', 'Arte'),
        ('otros', 'Otros'),
    ]
    
    CONDICIONES = [
        ('excelente', 'Excelente'),
        ('bueno', 'Bueno'),
        ('regular', 'Regular'),
        ('malo', 'Malo'),
    ]
    
    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True)
    titulo = models.CharField(max_length=300)
    subtitulo = models.CharField(max_length=300, blank=True, null=True)
    autor = models.CharField(max_length=200)
    editorial = models.CharField(max_length=200, blank=True, null=True)
    publicacion = models.IntegerField(validators=[MinValueValidator(1000), MaxValueValidator(9999)])
    edicion = models.CharField(max_length=50, blank=True, null=True)
    
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='otros')
    num_paginas = models.IntegerField(blank=True, null=True)
    idioma = models.CharField(max_length=50, default='Español')
    
    ubicacion = models.CharField(max_length=100, help_text="Ej: Estante A, Nivel 2")
    codigo_inventario = models.CharField(max_length=50, unique=True)
    condicion = models.CharField(max_length=20, choices=CONDICIONES, default='bueno')
    
    disponible = models.BooleanField(default=True)
    fecha_adquisicion = models.DateField(auto_now_add=True)
    precio_adquisicion = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    descripcion = models.TextField(blank=True, null=True)
    portada = models.ImageField(upload_to='portadas/', blank=True, null=True)
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Libro'
        verbose_name_plural = 'Libros'
        ordering = ['-creado_en']
    
    def __str__(self):
        return f"{self.titulo} - {self.autor}"


class Prestamo(models.Model):
    ESTADOS = [
        ('activo', 'Activo'),
        ('devuelto', 'Devuelto'),
        ('vencido', 'Vencido'),
        ('renovado', 'Renovado'),
    ]
    
    libro = models.ForeignKey(Libro, on_delete=models.PROTECT)
    
    alumno_nombre = models.CharField(max_length=200)
    alumno_matricula = models.CharField(max_length=50)
    alumno_grado = models.CharField(max_length=50, blank=True, null=True)
    alumno_grupo = models.CharField(max_length=10, blank=True, null=True)
    alumno_telefono = models.CharField(max_length=15, blank=True, null=True)
    
    fecha_prestamo = models.DateField(auto_now_add=True)
    fecha_vencimiento = models.DateField()
    fecha_devolucion_real = models.DateField(blank=True, null=True)
    
    activo = models.BooleanField(default=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='activo')
    renovaciones = models.IntegerField(default=0)
    
    notas_prestamo = models.TextField(blank=True, null=True)
    notas_devolucion = models.TextField(blank=True, null=True)
    
    tiene_multa = models.BooleanField(default=False)
    monto_multa = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    multa_pagada = models.BooleanField(default=False)
    
    prestado_por = models.CharField(max_length=100, blank=True, null=True)
    recibido_por = models.CharField(max_length=100, blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Préstamo'
        verbose_name_plural = 'Préstamos'
        ordering = ['-fecha_prestamo']
    
    def __str__(self):
        return f"{self.libro.titulo} - {self.alumno_nombre}"
    
    def save(self, *args, **kwargs):
        if not self.fecha_vencimiento:
            config = ConfiguracionSistema.load()
            fecha_inicio = self.fecha_prestamo if self.fecha_prestamo else timezone.now().date()
            self.fecha_vencimiento = fecha_inicio + timedelta(days=config.dias_prestamo)
        
        super().save(*args, **kwargs)
        
        self.libro.disponible = not self.activo
        self.libro.save()


class Multa(models.Model):
    TIPOS = [
        ('retraso', 'Retraso en devolución'),
        ('daño', 'Daño al libro'),
        ('perdida', 'Pérdida del libro'),
        ('otro', 'Otro'),
    ]
    
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('pagada', 'Pagada'),
        ('condonada', 'Condonada'),
    ]
    
    prestamo = models.ForeignKey(Prestamo, on_delete=models.CASCADE, blank=True, null=True)
    libro = models.ForeignKey(Libro, on_delete=models.PROTECT, blank=True, null=True)
    
    alumno_nombre = models.CharField(max_length=200)
    alumno_matricula = models.CharField(max_length=50)
    
    tipo = models.CharField(max_length=20, choices=TIPOS)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    
    descripcion = models.TextField()
    fecha_multa = models.DateField(auto_now_add=True)
    fecha_pago = models.DateField(blank=True, null=True)
    
    recibo = models.CharField(max_length=50, blank=True, null=True)
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Multa'
        verbose_name_plural = 'Multas'
        ordering = ['-fecha_multa']
    
    def __str__(self):
        return f"Multa #{self.id} - {self.alumno_nombre} - ${self.monto}"


class HistorialMovimiento(models.Model):
    TIPOS = [
        ('prestamo', 'Préstamo'),
        ('devolucion', 'Devolución'),
        ('renovacion', 'Renovación'),
        ('multa', 'Multa'),
        ('baja', 'Baja de libro'),
        ('alta', 'Alta de libro'),
    ]
    
    tipo = models.CharField(max_length=20, choices=TIPOS)
    libro = models.ForeignKey(Libro, on_delete=models.SET_NULL, blank=True, null=True)
    prestamo = models.ForeignKey(Prestamo, on_delete=models.SET_NULL, blank=True, null=True)
    
    alumno_nombre = models.CharField(max_length=200, blank=True, null=True)
    alumno_matricula = models.CharField(max_length=50, blank=True, null=True)
    
    descripcion = models.TextField()
    usuario_responsable = models.CharField(max_length=100)
    
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Historial de Movimiento'
        verbose_name_plural = 'Historial de Movimientos'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"


class ConfiguracionSistema(models.Model):
    dias_prestamo = models.IntegerField(default=15)
    max_renovaciones = models.IntegerField(default=2)
    max_prestamos_simultaneos = models.IntegerField(default=3)
    
    multa_por_dia = models.DecimalField(max_digits=10, decimal_places=2, default=5.00)
    dias_gracia = models.IntegerField(default=0)
    
    nombre_biblioteca = models.CharField(max_length=200, default="Biblioteca Cecytem")
    direccion = models.TextField(blank=True)
    telefono = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    horario = models.TextField(blank=True)
    
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Configuración del Sistema'
        verbose_name_plural = 'Configuración del Sistema'
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        pass
    
    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    def __str__(self):
        return f"Configuración - {self.nombre_biblioteca}"