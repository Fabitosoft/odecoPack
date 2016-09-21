from django.db import models

from importaciones.models import Moneda
from utils.models import TimeStampedModel
from productos.models import Producto
# Create your models here.

class Proveedor(TimeStampedModel):
    nombre = models.CharField(max_length=120, unique=True)
    moneda = models.ForeignKey(Moneda, on_delete=models.PROTECT)

    class Meta:
        verbose_name_plural = "proveedores"

    def __str__(self):
        return self.nombre

