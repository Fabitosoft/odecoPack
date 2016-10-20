from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from importaciones.models import Moneda
from utils.models import TimeStampedModel
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.factor_importacion_original = self.factor_importacion

    class Meta:
        verbose_name_plural = "1. Proveedores"

    def __str__(self):
        return self.nombre


@receiver(post_save, sender=Proveedor)
def post_save_proveedor(sender, instance, *args, **kwargs):
    tasa = instance.moneda.cambio
    print("Entro a cambiar factor de importacion")
    qsMxC = instance.mis_margenes_por_categoria.all()
    for MxC in qsMxC:
        qsPro = MxC.productos_con_margen.all()
        for producto in qsPro:
            producto.save(factor_importacion=instance.factor_importacion, tasa=tasa)


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
        return "%s - %s" % (self.proveedor, self.categoria)


@receiver(post_save, sender=MargenProvedor)
def post_save_margen_proveedor(sender, instance, *args, **kwargs):
    tasa = instance.proveedor.moneda.cambio
    factor_importacion = instance.proveedor.factor_importacion
    for producto in instance.productos_con_margen.all():
        producto.save(margen_deseado=instance.margen_deseado, tasa=tasa, factor_importacion=factor_importacion)

# endregion
