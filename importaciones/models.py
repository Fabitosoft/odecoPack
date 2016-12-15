from django.db import models

# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver


class Moneda(models.Model):
    nombre = models.CharField(max_length=20, unique=True)
    cambio = models.DecimalField(max_digits=18, decimal_places=4, default=0)

    class Meta:
        verbose_name_plural = "1. Monedas"

    def __str__(self):
        return '%s' % self.nombre


@receiver(post_save, sender=Moneda)
def post_save_margen_proveedor(sender, instance, *args, **kwargs):
    print("Entro a Actualizar tasa de Cambio")
    qs = instance.provedores_con_moneda.all()
    for provedor in qs:
        qs2 = provedor.mis_margenes_por_categoria.all()
        for mxc in qs2:
            productosqs = mxc.productos_con_margen.all()
            for producto in productosqs:
                producto.save(tasa=instance.cambio)
            qsArt = mxc.articulos_catalogo_con_margen.all()
            for articulo_catalogo in qsArt:
                articulo_catalogo.save(tasa=instance.cambio)
