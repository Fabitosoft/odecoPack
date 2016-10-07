from django.db import models

# Create your models here.
from empresas.models import Canal
from importaciones.models import Moneda
from productos.models import Producto
from proveedores.models import Proveedor
from utils.models import TimeStampedModel

class FormaPago(models.Model):
    canal = models.ForeignKey(Canal)
    forma = models.CharField(max_length=100)

    class Meta:
        unique_together = ("canal","forma")
        verbose_name_plural = "Formas de Pago"

    def __str__(self):
        return "%s %s"%(self.canal,self.forma)

class ListaPrecio(TimeStampedModel):
    proveedor = models.ForeignKey(Proveedor)
    producto = models.ForeignKey(Producto, related_name="en_lista_precios")
    cantidad_minima=models.DecimalField(max_digits=10, decimal_places=3)
    valor = models.DecimalField(max_digits=10, decimal_places=3)

    class Meta:
        unique_together = ("proveedor","producto", "cantidad_minima")
        verbose_name_plural = "listas de precios"


class VariableListaPrecio(TimeStampedModel):
    forma_pago = models.OneToOneField(FormaPago, related_name='porcentaje_lp')
    value = models.DecimalField(max_digits=10, decimal_places=3)

    class Meta:
        verbose_name_plural = "Variables Lista Precios Formas Pago"

    def __str__(self):
        return "%s" %(self.forma_pago)

class VariableBasica(TimeStampedModel):
    moneda_origen = models.OneToOneField(Moneda)
    factor_importacion = models.DecimalField(max_digits=10, decimal_places=3)
    margen_deseado = models.DecimalField(max_digits=10, decimal_places=3)

    def __str__(self):
        return "%s" %(self.moneda_origen)