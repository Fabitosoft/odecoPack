from django.db import models
from biable.models import (
    ItemsBiable,
    Cliente,
    SucursalBiable,
    VendedorBiable,
    CiudadBiable
)


# Create your models here.
class HistoricoVenta(models.Model):
    cliente = models.ForeignKey(Cliente, null=True, blank=True)
    item_biable = models.ForeignKey(ItemsBiable, null=True, blank=True)
    sucursal = models.ForeignKey(SucursalBiable, null=True, blank=True)
    vendedor = models.ForeignKey(VendedorBiable, null=True, blank=True)
    ciudad = models.ForeignKey(CiudadBiable, null=True, blank=True)
    dia = models.IntegerField(null=True, blank=True)
    mes = models.IntegerField(null=True, blank=True)
    semana = models.IntegerField(null=True, blank=True)
    dia_semana = models.IntegerField(null=True, blank=True)
    t_3_venta_neta = models.DecimalField(decimal_places=0, max_digits=10, default=0)
    t_2_venta_neta = models.DecimalField(decimal_places=0, max_digits=10, default=0)
    t_1_venta_neta = models.DecimalField(decimal_places=0, max_digits=10, default=0)
    t_venta_neta = models.DecimalField(decimal_places=0, max_digits=10, default=0)
    t_3_venta_neta_acum = models.DecimalField(decimal_places=0, max_digits=10, default=0)
    t_2_venta_neta_acum = models.DecimalField(decimal_places=0, max_digits=10, default=0)
    t_1_venta_neta_acum = models.DecimalField(decimal_places=0, max_digits=10, default=0)
    t_venta_neta_acum = models.DecimalField(decimal_places=0, max_digits=10, default=0)
