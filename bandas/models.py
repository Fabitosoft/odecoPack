from decimal import Decimal
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

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

    con_empujador = models.BooleanField(default=False)
    empujador_tipo = models.ForeignKey(ValorCaracteristica, null=True, blank=True,
                                       related_name="bandas_con_tipo_empujador", verbose_name="Tipo")
    empujador_altura = models.DecimalField(max_digits=18, null=True, blank=True, decimal_places=2,
                                           verbose_name="Altura (mm)")
    empujador_ancho = models.DecimalField(max_digits=18, null=True, blank=True, decimal_places=2,
                                          verbose_name="Ancho (mm)")
    empujador_distanciado = models.PositiveIntegerField(null=True, blank=True, verbose_name="Distanciado")
    empujador_identacion = models.DecimalField(max_digits=18, null=True, blank=True, decimal_places=2,
                                               verbose_name="Identacion (mm)")
    empujador_filas_entre = models.PositiveIntegerField(null=True, blank=True, verbose_name="Filas entre Empujador")
    empujador_total_filas = models.PositiveIntegerField(null=True, blank=True, verbose_name="Total Filas Empujador")

    con_aleta = models.BooleanField(default=False)
    aleta = models.DecimalField(max_digits=18, null=True, blank=True, decimal_places=2, verbose_name="Aleta (mm)")
    aleta_identacion = models.DecimalField(max_digits=18, null=True, blank=True, decimal_places=2,
                                           verbose_name="Identacion Aleta (mm)")

    descripcion_estandar = models.CharField(max_length=200)
    descripcion_comercial = models.CharField(max_length=200)
    referencia = models.CharField(max_length=120, unique=True,null=True, blank=True)
    fabricante = models.CharField(max_length=60)
    created_by = models.ForeignKey(User, editable=False, null=True, blank=True, related_name="banda_created_by")
    updated_by = models.ForeignKey(User, editable=False, null=True, blank=True, related_name="banda_updated_by")

    activo = models.BooleanField(default=False)

    precio_total = models.DecimalField(max_digits=18, decimal_places=4, default=0)

    ensamblaje = models.ManyToManyField(
        Producto,
        through='Ensamblado',
        through_fields=('banda', 'producto'),
    )

    def get_absolute_url(self):
        return reverse("bandas:detalle_banda", kwargs={"pk": self.pk})

    def save(self):
        self.actualizar_precio_total()
        super().save()

    def actualizar_precio_total(self):
        precio = 0
        for modulo in self.ensamblado.all():
            precio += modulo.precio_linea
        self.precio_total = precio


class Ensamblado(TimeStampedModel):
    banda = models.ForeignKey(Banda, on_delete=models.CASCADE, related_name='ensamblado')
    producto = models.ForeignKey(Producto,on_delete=models.CASCADE, related_name='ensamblados')
    ancho = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="Ancho (mm)")
    precio_linea = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    cortado_a = models.CharField(max_length=10)
    cantidad = models.DecimalField(max_digits=18, decimal_places=2)
    created_by = models.ForeignKey(User, editable=False, null=True, blank=True, related_name="ensamblado_created_by")
    updated_by = models.ForeignKey(User, editable=False, null=True, blank=True, related_name="ensamblado_updated_by")

    def save(self):
        self.actualizar_precio_total_linea()
        super().save()
        self.banda.save()

    def actualizar_precio_total_linea(self):
        self.precio_linea = Decimal(self.producto.precio_base) * Decimal(self.cantidad)
