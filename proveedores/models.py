from django.db import models


from utils.models import TimeStampedModel
from productos.models import Producto
# Create your models here.

class Moneda(models.Model):
    nombre = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.nombre

class Proveedor(TimeStampedModel):
    nombre = models.CharField(max_length=120, unique=True)
    moneda = models.ForeignKey(Moneda, on_delete=models.PROTECT)

    def __str__(self):
        return self.nombre

class ListaPrecio(TimeStampedModel):
    proveedor = models.ForeignKey(Proveedor)
    producto = models.ForeignKey(Producto)
    cantidad_minima=models.DecimalField(max_digits=10, decimal_places=3)
    valor = models.DecimalField(max_digits=10, decimal_places=3)

    class Meta:
        unique_together = ("producto", "cantidad_minima")
