from django.db import models

# Create your models here.

class Moneda(models.Model):
    nombre = models.CharField(max_length=20, unique=True)
    cambio = models.DecimalField(max_digits=18, decimal_places=4, default=0)

    class Meta:
        verbose_name_plural = "1. Monedas"

    def __str__(self):
        return '%s' % self.nombre
