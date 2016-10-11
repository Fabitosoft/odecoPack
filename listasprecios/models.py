from django.db import models

# Create your models here.
from empresas.models import Canal
from importaciones.models import Moneda
from utils.models import TimeStampedModel

class FormaPago(models.Model):
    canal = models.ForeignKey(Canal)
    forma = models.CharField(max_length=100)

    class Meta:
        unique_together = ("canal","forma")
        verbose_name_plural = "Formas de Pago"

    def __str__(self):
        return "%s %s"%(self.canal,self.forma)


class VariableListaPrecio(TimeStampedModel):
    forma_pago = models.OneToOneField(FormaPago, related_name='porcentaje_lp')
    value = models.DecimalField(max_digits=18, decimal_places=3)

    class Meta:
        verbose_name_plural = "Variables Lista Precios Formas Pago"

    def __str__(self):
        return "%s" % self.forma_pago

######################################################################################################################
# Categorias productos
######################################################################################################################
class CategoriaMargen(TimeStampedModel):
    nombre = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.nombre