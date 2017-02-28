from django.db import models

from importaciones.models import Moneda
from model_utils.models import TimeStampedModel
from productos_categorias.models import CategoriaProducto


# Create your models here.

# region Proveedor
class Proveedor(TimeStampedModel):
    nombre = models.CharField(max_length=120, unique=True)
    moneda = models.ForeignKey(Moneda, on_delete=models.PROTECT, related_name="provedores_con_moneda")
    factor_importacion = models.DecimalField(max_digits=18, decimal_places=3, default=1)
    margenes = models.ManyToManyField(
        CategoriaProducto,
        through='MargenProvedor',
        through_fields=('proveedor', 'categoria')
    )

    class Meta:
        verbose_name_plural = "1. Proveedores"

    def __str__(self):
        return self.nombre


# endregion

# region Margen por Proveedor
class MargenProvedor(TimeStampedModel):
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.CASCADE, related_name="mis_margenes_por_proveedor")
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name="mis_margenes_por_categoria")
    margen_deseado = models.DecimalField(max_digits=18, decimal_places=3, verbose_name="Margen (%)")

    class Meta:
        verbose_name_plural = "2. Margenes x Categoría x Proveedores"
        unique_together = ("categoria", "proveedor")

    def __str__(self):
        return "%s - %s" % (self.proveedor.nombre, self.categoria.nombre)

# endregion
