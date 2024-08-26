from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

class Mascota(models.Model):
    nombre = models.CharField(max_length=50)
    foto = models.ImageField(upload_to='administra')
    edad = models.IntegerField()
    genero = models.CharField(max_length=12)
    raza = models.CharField(max_length=100)
    descripcion = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'mascota'
        verbose_name_plural = 'mascotas'

    def __str__(self):
        return self.nombre

    def eliminar_con_historial(self, motivo_eliminacion):
        HistorialMascota.objects.create(
            nombre=self.nombre,
            foto=self.foto,
            edad=self.edad,
            genero=self.genero,
            raza=self.raza,
            descripcion=self.descripcion,
            motivo_eliminacion=motivo_eliminacion,
            fecha_eliminacion=timezone.now(),  
        )
        self.delete()

class HistorialMascota(models.Model):
    nombre = models.CharField(max_length=50)
    foto = models.ImageField(upload_to='historial_mascotas')
    edad = models.IntegerField()
    genero = models.CharField(max_length=12)
    raza = models.CharField(max_length=100)
    descripcion = models.TextField()
    motivo_eliminacion = models.TextField()
    fecha_eliminacion = models.DateTimeField(default=timezone.now)  

    class Meta:
        verbose_name = 'historial mascota'
        verbose_name_plural = 'historial mascotas'

    def __str__(self):
        return f'{self.nombre} (Eliminada el {self.fecha_eliminacion})'
