from datetime import datetime

from django.db import models


# Create your models here.

class VendedorBiable(models.Model):
    LINEAS = (
        (1, 'Proyectos'),
        (2, 'Bandas y Componentes'),
        (3, 'Posventa'),
        (4, 'Sin Definir'),
    )
    id = models.PositiveIntegerField(primary_key=True, editable=False)
    nombre = models.CharField(max_length=200)
    linea = models.PositiveIntegerField(choices=LINEAS, default=4)

    def __str__(self):
        return self.nombre


class MovimientoVentaBiable(models.Model):
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    day = models.PositiveIntegerField()
    vendedor = models.ForeignKey(VendedorBiable,null=True)
    id_terc_fa = models.CharField(max_length=20)
    cliente = models.CharField(max_length=200)
    proyecto = models.CharField(max_length=10)
    item_id = models.PositiveIntegerField()
    precio_uni = models.DecimalField(max_digits=18, decimal_places=4)
    cantidad = models.DecimalField(max_digits=18, decimal_places=4)
    venta_bruta = models.DecimalField(max_digits=18, decimal_places=4)
    dscto_netos = models.DecimalField(max_digits=18, decimal_places=4)
    costo_total = models.DecimalField(max_digits=18, decimal_places=4)
    rentabilidad = models.DecimalField(max_digits=18, decimal_places=4)
    imp_netos = models.DecimalField(max_digits=18, decimal_places=4)
    venta_neto = models.DecimalField(max_digits=18, decimal_places=4)

    class Meta:
        permissions = (
            ('ver_ventaxvendedor', 'Ver Ventas x Vendedor'),
            ('ver_ventaxcliente', 'Ver Ventas x Cliente'),
            ('ver_ventaxclientexano', 'Ver Ventas x Cliente x Año'),
            ('ver_ventaxmes', 'Ver Ventas x Mes'),
            ('ver_ventaxlineaxano', 'Ver Ventas x Linea x Año'),
            ('ver_ventaxlineaxanoxmes', 'Ver Ven. x Lin x Año x Mes'),
            ('ver_indicadores_ventas', 'Ver Indicadores de Ventas'),
        )
