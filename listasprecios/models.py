from django.db import models

# Create your models here.
from empresas.models import Canal
from importaciones.models import Moneda
from utils.models import TimeStampedModel


class FormaPago(models.Model):
    canal = models.ForeignKey(Canal)
    forma = models.CharField(max_length=100)
    porcentaje = models.DecimalField(max_digits=18, decimal_places=3, verbose_name="%", default=0)

    class Meta:
        unique_together = ("canal", "forma")
        verbose_name_plural = "1. Formas de Pago"

    def __str__(self):
        return "%s %s" % (self.canal, self.forma)


# region Margen por Categoría

class CategoriaMargen(TimeStampedModel):
    nombre = models.CharField(max_length=60, unique=True)

    class Meta:
        verbose_name_plural = "2. Margenes x Categoría"

    def __str__(self):
        return self.nombre

# endregion
