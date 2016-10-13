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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.factor_importacion_original = self.factor_importacion

    def save(self):
        super().save()
        if self.factor_importacion_original!= self.factor_importacion:
            tasa = self.moneda.moneda_cambio.cambio
            print("Entro a cambiar factor de importacion")
            qsMxC = self.mis_margenes_por_categoria.all()
            for MxC in qsMxC:
                qsPro = MxC.productos_con_margen.all()
                for producto in qsPro:
                    producto.save(factor_importacion=self.factor_importacion, tasa = tasa)

    class Meta:
        verbose_name_plural = "1. Proveedores"

    def __str__(self):
        return self.nombre


class MargenProvedor(TimeStampedModel):
    categoria = models.ForeignKey(CategoriaMargen, on_delete=models.CASCADE, related_name="mis_margenes_por_proveedor")
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name="mis_margenes_por_categoria")
    margen_deseado = models.DecimalField(max_digits=18, decimal_places=3, verbose_name="Margen (%)")

    def save(self):
        super().save()
        tasa = self.proveedor.moneda.moneda_cambio.cambio
        factor_importacion = self.proveedor.factor_importacion
        for producto in self.productos_con_margen.all():
            producto.save(margen_deseado=self.margen_deseado, tasa=tasa, factor_importacion=factor_importacion)

    class Meta:
        verbose_name_plural = "2. Margenes x Categoría x Proveedores"
        unique_together = ("categoria", "proveedor")

    def __str__(self):
        return "%s - %s" % (self.proveedor, self.categoria)
