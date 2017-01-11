from django.db import models

from model_utils.models import TimeStampedModel

from biable.models import Cliente, FacturasBiable


# Create your models here.
class EnvioTransportadoraTCC(TimeStampedModel):
    TIPO_ENVIO = (
        ('PQ', 'Paquetería'),
        ('MS', 'Mensajería')
    )
    ESTADO_ENTREGA = (
        ('CP', 'Cumplido parcial del despacho por presentar novedad'),
        ('DD', 'Descargado en Destino'),
        ('PE', 'En proceso de entrega'),
        ('RP', 'En Reparto'),
        ('EN', 'Entregada'),
        ('ER', 'Entregada (Retorno Odeco)'),
        ('NS', 'Novedad Solucionada'),
        ('RO', 'Recibido en Origen'),
        ('NA', 'NO FUE ENVIADA')
    )
    FORMA_PAGO = (
        ('NOR', 'NORMAL'),
        ('CTA', 'CUENTA'),
        ('RD', 'RD'),
        ('FCE', 'FCE'),
        ('NA', 'NO VIAJA'),
        ('9AM', '9AM'),
    )

    fecha_envio = models.DateField()
    fecha_entrega = models.DateField(null=True, blank=True)
    nro_factura_transportadora = models.PositiveIntegerField(null=True, blank=True)
    nro_tracking = models.CharField(max_length=60)
    cliente = models.ForeignKey(Cliente, null=True, blank=True)
    cliente_alternativo = models.CharField(max_length=60, null=True, blank=True)
    tipo = models.CharField(max_length=2, choices=TIPO_ENVIO, default='PQ')
    servicio_boom = models.BooleanField(default=False)
    rr = models.BooleanField(default=False, verbose_name='Entregado RR')
    forma_pago = models.CharField(max_length=3, choices=FORMA_PAGO)
    observacion = models.TextField(max_length=200, blank=True, null=True)
    estado = models.CharField(max_length=2, choices=ESTADO_ENTREGA)
    valor = models.DecimalField(decimal_places=2, max_digits=18)
    facturas = models.ManyToManyField(FacturasBiable, related_name='envios', blank=True)
