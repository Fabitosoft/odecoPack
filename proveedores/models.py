from django.db import models

from importaciones.models import Moneda
from utils.models import TimeStampedModel
from listasprecios.models import CategoriaMargen


# Create your models here.

class Proveedor(TimeStampedModel):
    nombre = models.CharField(max_length=120, unique=True)
    moneda = models.ForeignKey(Moneda, on_delete=models.PROTECT, related_name="provedores_con_moneda")
    factor_importacion = models.DecimalField(max_digits=18, decimal_places=3, default=1)
    margenes = models.ManyToManyField(
        CategoriaMargen,
        through='MargenProvedor',
        through_fields=('proveedor', 'categoria')
    )

    def save(self):
        super().save()
        qsMxC = self.mis_margenes_por_categoria.all()
        for MxC in qsMxC:
            qsPro = MxC.productos_con_margen.all()
            for producto in qsPro:
                producto.save()

    class Meta:
        verbose_name_plural = "proveedores"

    def __str__(self):
        return self.nombre


class MargenProvedor(models.Model):
    categoria = models.ForeignKey(CategoriaMargen, on_delete=models.CASCADE, related_name="mis_margenes_por_proveedor")
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name="mis_margenes_por_categoria")
    margen_deseado = models.DecimalField(max_digits=18, decimal_places=3, verbose_name="Margen (%)")

    def save(self):
        super().save()
        for producto in self.productos_con_margen.all():
            producto.save()

    class Meta:
        verbose_name_plural = "Margenes x Categoría x Proveedores"
        unique_together = ("categoria", "proveedor")

    def __str__(self):
        return "%s - %s" % (self.proveedor, self.categoria)
