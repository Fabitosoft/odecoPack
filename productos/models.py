from django.db import models
from utils.models import TimeStampedModel

# Create your models here.
class UnidadMedida(models.Model):
    nombre = models.CharField(max_length=120)

    def __str__(self):
        return self.nombre

class Producto(TimeStampedModel):
    id_cguno = models.PositiveIntegerField()
    referencia = models.CharField(max_length=120, unique=True)
    descripcion_estandar = models.CharField(max_length=200)
    descripcion_comercial = models.CharField(max_length=200)
    fabricante = models.CharField(max_length=60, null=True, blank=True)
    cantidad_empaque = models.DecimalField(max_digits=10,decimal_places=4, default=0)
    unidad_medida = models.ForeignKey(UnidadMedida,on_delete=models.PROTECT, null=True)

    def __str__(self):
        return self.descripcion_estandar
