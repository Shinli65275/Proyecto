from django.db import models

class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=100)
    publicacion = models.IntegerField()
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo