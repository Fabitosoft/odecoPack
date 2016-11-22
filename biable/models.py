from datetime import datetime

from django.db import models


# Create your models here.

class VendedorBiable(models.Model):
    LINEAS = (
        (1, 'Proyectos'),
        (2, 'Bandas y Componentes'),
        (3, 'Proyectos'),
        (4, 'Sin Definir'),
    )
    id = models.PositiveIntegerField(primary_key=True, editable=False)
    nombre = models.CharField(max_length=200)
    linea = models.PositiveIntegerField(choices=LINEAS, default=4)

    def __str__(self):
        return self.nombre


class DataBiable(models.Model):
    vende_nombre = models.CharField(max_length=120, blank=True, null=True)
    vende_id = models.PositiveIntegerField(blank=True, null=True)
    tipo_docu_id = models.CharField(max_length=10, blank=True, null=True)
    cli_nit = models.CharField(max_length=16, blank=True, null=True)
    item_descripcion = models.CharField(max_length=200, blank=True, null=True)
    tipo_doc_descripcion = models.CharField(max_length=50, blank=True, null=True)
    proyecto_id = models.CharField(max_length=50, blank=True, null=True)
    documento_fc = models.CharField(max_length=50, blank=True, null=True)
    cli_raz_social = models.CharField(max_length=120, blank=True, null=True)
    item_id = models.PositiveIntegerField(blank=True, null=True)
    fecha_registro = models.DateField(default=datetime.now)
    tipo_documento_relacionado = models.CharField(max_length=10, blank=True, null=True)
    nro_documento_relacionado = models.PositiveIntegerField(blank=True, null=True)
    tipo_rm_relacionado = models.CharField(max_length=10, blank=True, null=True)
    nro_rm_relacionado = models.PositiveIntegerField(blank=True, null=True)
    valor_bruto = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    descuentos_netos = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    impuestos_netos = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    valor_neto = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    costo = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    rentabilidad = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    fecha_generacion_biable = models.DateField(default=datetime.now)
    numero_registros = models.PositiveIntegerField(default=0)
