from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from model_utils.models import TimeStampedModel

from biable.models import Cliente, FacturasBiable
from geografia_colombia.models import Ciudad


# Create your models here.
class EnvioTransportadoraTCCQuerySet(models.QuerySet):
    def con_boom(self):
        return self.filter(
            ~Q(nro_tracking_boom__exact='')
            &
            Q(fecha_entrega_boom__isnull=True)
        )

    def con_entrega(self):
        return self.filter(
            Q(fecha_entrega__isnull=True)
        )


class EnvioTransportadoraTCCPendientesManager(models.Manager):
    def get_queryset(self):
        return EnvioTransportadoraTCCQuerySet(self.model, using=self._db).filter(
            (
                ~Q(nro_tracking_boom__exact='') &
                Q(fecha_entrega_boom__isnull=True)
            )
            |
            Q(fecha_entrega__isnull=True)
        )

    def boom(self):
        qs1 = self.get_queryset().con_boom()
        qs2 = self.get_queryset().con_entrega()
        qsF = qs1.exclude(pk__in=qs2)
        return qsF

    def entrega(self):
        qs1 = self.get_queryset().con_boom()
        qs2 = self.get_queryset().con_entrega()
        qsF = qs2.exclude(pk__in=qs1)
        return qsF

    def entrega_boom(self):
        qs1 = self.get_queryset().con_boom()
        qs2 = self.get_queryset().con_entrega()
        qsF = self.get_queryset().filter(
            Q(pk__in=qs1) &
            Q(pk__in=qs2)
        ).distinct()
        return qsF


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
    nro_tracking_boom = models.CharField(max_length=60, blank=True, null=True)
    fecha_entrega_boom = models.DateField(null=True, blank=True)
    forma_pago = models.CharField(max_length=3, choices=FORMA_PAGO)
    observacion = models.TextField(max_length=200, blank=True, null=True)
    estado = models.CharField(max_length=2, choices=ESTADO_ENTREGA)
    valor = models.DecimalField(decimal_places=2, max_digits=18, null=True, blank=True)
    valor_boom = models.DecimalField(decimal_places=2, max_digits=18, null=True, blank=True)
    facturas = models.ManyToManyField(FacturasBiable, related_name='envios', blank=True, verbose_name='Facturas')
    ciudad = models.ForeignKey(Ciudad, related_name='mis_envios_tcc', on_delete=models.PROTECT)

    objects = models.Manager()
    pendientes = EnvioTransportadoraTCCPendientesManager()

    class Meta:
        permissions = (
            ('ver_segui_envio_tcc', 'Seg. Envios TCC'),
        )

    def get_numero_dias_entrega(self):
        if self.fecha_entrega:
            dias = (abs((self.fecha_entrega - self.fecha_envio).days))
            if dias > 1:
                return "%s días" % (dias)
            else:
                return "%s día" % (dias)
        return "Sin Entregar"

    def get_numero_dias_desde_envio(self):
        fecha_actual = timezone.now().date()
        if not self.fecha_entrega:
            dias = (abs((fecha_actual - self.fecha_envio).days))
            if dias > 1:
                return "%s días" % (dias)
            else:
                return "%s día" % (dias)
        return "Entregada"

    def get_numero_dias_entrega_boom(self):
        if self.nro_tracking_boom:
            if self.fecha_entrega_boom:
                dias = (abs((self.fecha_entrega_boom - self.fecha_envio).days))
                if dias > 1:
                    return "%s días" % (dias)
                else:
                    return "%s día" % (dias)
            return "Sin Entregar"
        return ""

    def get_numero_dias_desde_envio_boom(self):
        if self.nro_tracking_boom:
            fecha_actual = timezone.now().date()
            if not self.fecha_entrega_boom:
                dias = (abs((fecha_actual - self.fecha_envio).days))
                if dias > 1:
                    return "%s días" % (dias)
                else:
                    return "%s día" % (dias)
            return "Entregada"
        return ""

    def get_absolute_update_url(self):
        return reverse("despacho_mercancia:envio-update", kwargs={"pk": self.pk})

    def get_absolute_url(self):
        return reverse("despacho_mercancia:envio-detail", kwargs={"pk": self.pk})
