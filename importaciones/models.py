from django.db import models

# Create your models here.
class Moneda(models.Model):
    nombre = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.nombre


class FactorCambioMoneda(models.Model):
    moneda_origen = models.OneToOneField(Moneda, related_name="moneda_cambio")
    cambio = models.DecimalField(max_digits=10,decimal_places=4)

    class Meta:
        verbose_name_plural = "Factores de Cambio Monedas"

    def __str__(self):
        return '%s vs COP'%(self.moneda_origen)