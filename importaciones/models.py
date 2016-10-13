from django.db import models


# Create your models here.
class Moneda(models.Model):
    nombre = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.nombre


class FactorCambioMoneda(models.Model):
    moneda_origen = models.OneToOneField(Moneda, related_name="moneda_cambio")
    cambio = models.DecimalField(max_digits=18, decimal_places=4)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cambio_original = self.cambio

    def save(self):
        super().save()
        if self.cambio != self.cambio_original:
            print("Entro a Actualizar tasa de Cambio")
            qs = self.moneda_origen.provedores_con_moneda.all()
            for provedor in qs:
                qs2 = provedor.mis_margenes_por_categoria.all()
                for mxc in qs2:
                    productosqs = mxc.productos_con_margen.all()
                    for producto in productosqs:
                        producto.save(tasa=self.cambio)

    class Meta:
        verbose_name_plural = "Factores de Cambio Monedas"

    def __str__(self):
        return '%s vs COP' % self.moneda_origen
