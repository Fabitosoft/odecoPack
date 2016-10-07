from django.contrib.auth.models import User
from django.db import models

from utils.models import TimeStampedModel
from productos.models import Producto


# Create your models here.
class Caracteristica(models.Model):
    nombre = models.CharField(max_length=60)

    def __str__(self):
        return self.nombre


class ValorCaracteristica(models.Model):
    caracteristica = models.ForeignKey(Caracteristica)
    nombre = models.CharField(max_length=60)
    nomenclatura = models.CharField(max_length=3, blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Banda(TimeStampedModel):
    serie = models.ForeignKey(ValorCaracteristica, related_name="bandas_con_serie")
    tipo = models.ForeignKey(ValorCaracteristica, related_name="bandas_con_tipo")
    material = models.ForeignKey(ValorCaracteristica, related_name="bandas_con_material")
    color = models.ForeignKey(ValorCaracteristica, related_name="bandas_con_color")
    ancho = models.DecimalField(decimal_places=2, max_digits=8, verbose_name="Ancho (mm)")
    longitud = models.DecimalField(decimal_places=2, max_digits=8, verbose_name="Longitud (mm)")
    material_varilla = models.ForeignKey(ValorCaracteristica, related_name="bandas_con_material_varilla")
    total_filas = models.PositiveIntegerField()

    empujador = models.ForeignKey(ValorCaracteristica, related_name="bandas_con_empujador")
    empujador_tipo = models.ForeignKey(ValorCaracteristica, null=True, blank=True,
                                       related_name="bandas_con_tipo_empujador", verbose_name="Tipo")
    empujador_altura = models.DecimalField(max_digits=10, null=True, blank=True, decimal_places=2,
                                           verbose_name="Altura (mm)")
    empujador_ancho = models.DecimalField(max_digits=10, null=True, blank=True, decimal_places=2,
                                          verbose_name="Ancho (mm)")
    empujador_distanciado = models.PositiveIntegerField(null=True, blank=True, verbose_name="Distanciado")
    empujador_identacion = models.DecimalField(max_digits=10, null=True, blank=True, decimal_places=2,
                                               verbose_name="Identacion (mm)")
    empujador_filas_entre = models.PositiveIntegerField(null=True, blank=True, verbose_name="Filas entre Empujador")
    empujador_total_filas = models.PositiveIntegerField(null=True, blank=True, verbose_name="Total Filas Empujador")
    aleta = models.DecimalField(max_digits=10, null=True, blank=True, decimal_places=2, verbose_name="Aleta (mm)")
    aleta_identacion = models.DecimalField(max_digits=10, null=True, blank=True, decimal_places=2,
                                           verbose_name="Identacion Aleta (mm)")

    descripcion_estandar = models.CharField(max_length=200)
    descripcion_comercial = models.CharField(max_length=200)
    referencia = models.CharField(max_length=120, unique=True)
    fabricante = models.CharField(max_length=60)
    created_by = models.ForeignKey(User, editable=False, null=True, blank=True, related_name="banda_created_by")
    updated_by = models.ForeignKey(User, editable=False, null=True, blank=True, related_name="banda_updated_by")

    ensamblaje = models.ManyToManyField(
        Producto,
        through='Ensamblado',
        through_fields=('banda', 'producto'),
    )


class Ensamblado(TimeStampedModel):
    banda = models.ForeignKey(Banda, on_delete=models.CASCADE, related_name='ensamblado')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='ensamblados')
    ancho = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ancho (mm)")
    cortado_a = models.CharField(max_length=10)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    created_by = models.ForeignKey(User, editable=False, null=True, blank=True, related_name="ensamblado_created_by")
    updated_by = models.ForeignKey(User, editable=False, null=True, blank=True, related_name="ensamblado_updated_by")
