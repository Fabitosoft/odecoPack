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

    class Meta:
        verbose_name_plural = "proveedores"

    def __str__(self):
        return self.nombre

# class FactoresImportacion(TimeStampedModel):
#     nombre = models.CharField

class ListaPrecio(TimeStampedModel):
    proveedor = models.ForeignKey(Proveedor)
    producto = models.ForeignKey(Producto)
    cantidad_minima=models.DecimalField(max_digits=10, decimal_places=3)
    valor = models.DecimalField(max_digits=10, decimal_places=3)

    class Meta:
        unique_together = ("proveedor","producto", "cantidad_minima")
        verbose_name_plural = "listas de precios"

    def __str__(self):
        return "%s %s %s"%(self.proveedor,self.producto.referencia, self.cantidad_minima)

class VariableListaPrecio(TimeStampedModel):
    referencia = models.CharField(max_length=15, unique=True)
    nombre = models.CharField(max_length=120, unique=True)
    value = models.DecimalField(max_digits=10, decimal_places=3)

    class Meta:
        verbose_name_plural = "Variables Lista Precios"

    def __str__(self):
        return "%s" %(self.nombre)


