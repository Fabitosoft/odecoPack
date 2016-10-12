from django.db import models

from utils.models import TimeStampedModel


# Create your models here.

class Canal(TimeStampedModel):
    canal = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "canales"

    def __str__(self):
        return self.canal


class GrupoEmpresarial(TimeStampedModel):
    nombre = models.CharField(max_length=200, unique=True)

    class Meta:
        verbose_name_plural = "grupos empresariales"

    def __str__(self):
        return self.nombre


class Empresa(TimeStampedModel):
    nombre = models.CharField(max_length=200, unique=True)
    nit = models.CharField(max_length=50, unique=True)
    canal = models.ForeignKey(Canal, on_delete=models.PROTECT, related_name="empresas")
    grupo_empresarial = models.ForeignKey(GrupoEmpresarial, related_name="empresas", null=True, blank=True)

    class Meta:
        verbose_name_plural = "empresas"

    def __str__(self):
        return self.nombre
