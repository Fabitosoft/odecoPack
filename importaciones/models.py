from django.db import models

# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver


class Moneda(models.Model):
    nombre = models.CharField(max_length=20, unique=True)

    class Meta:
        verbose_name_plural = "1. Monedas"

    def __str__(self):
        return self.nombre


class FactorCambioMoneda(models.Model):
    moneda_origen = models.OneToOneField(Moneda, related_name="moneda_cambio")
    cambio = models.DecimalField(max_digits=18, decimal_places=4)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cambio_original = self.cambio

    class Meta:
        verbose_name_plural = "2. Tasas de Cambio Monedas"

    def __str__(self):
        return '%s vs COP' % self.moneda_origen


@receiver(post_save, sender=FactorCambioMoneda)
def post_save_margen_proveedor(sender, instance, *args, **kwargs):
    print("Entro a Actualizar tasa de Cambio")
    qs = instance.moneda_origen.provedores_con_moneda.all()
    for provedor in qs:
        qs2 = provedor.mis_margenes_por_categoria.all()
        for mxc in qs2:
            productosqs = mxc.productos_con_margen.all()
            for producto in productosqs:
                producto.save(tasa=instance.cambio)
