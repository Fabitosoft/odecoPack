from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.signals import post_save
from django.urls import reverse

from model_utils.models import TimeStampedModel
from cotizaciones.models import Cotizacion
from despachos_mercancias.models import EnvioTransportadoraTCC
from biable.models import FacturasBiable


# Create your models here.
class Tarea(TimeStampedModel):
    ESTADOS = (
        (0, 'Pendiente'),
        (1, 'Atendida en Proceso'),
        (2, 'Atendida Terminada'),
    )
    estado = models.PositiveIntegerField(choices=ESTADOS, default=0)
    descripcion = models.TextField(max_length=400, null=True, blank=True)

    class Meta:
        abstract = True


# region Tarea Cotizacion
class TareaCotizacion(Tarea):
    cotizacion = models.OneToOneField(Cotizacion, related_name='tarea', null=True, blank=True,
                                      on_delete=models.SET_NULL)

    def get_descripcion_tarea(self):
        descripcion = "Cotizacion %s con estado %s" % (
            self.cotizacion.nro_cotizacion, self.cotizacion.get_estado_display())
        return descripcion


class SeguimientoCotizacion(TimeStampedModel):
    observacion = models.TextField(max_length=300)
    tarea = models.ForeignKey(TareaCotizacion, related_name='seguimientos')


# endregion

# region EnvioTCC
class TareaEnvioTCC(Tarea):
    envio = models.OneToOneField(EnvioTransportadoraTCC, related_name='tarea', null=True, blank=True,
                                 on_delete=models.SET_NULL)

    def get_descripcion_tarea(self):
        facturas = ""
        for factura in self.envio.facturas.all():
            nro_factura = "(%s-%s)" % (factura.tipo_documento, factura.nro_documento)
            facturas += nro_factura
        descripcion = "Envio TCC con facturas: %s. NRO Seguimiento: %s" % (facturas, self.envio.nro_tracking)
        return descripcion


class SeguimientoEnvioTCC(TimeStampedModel):
    observacion = models.TextField(max_length=300)
    tarea = models.ForeignKey(TareaEnvioTCC, related_name='seguimientos')


# enregion


# region TareaCartera
class TareaCartera(Tarea):
    factura = models.OneToOneField(FacturasBiable, related_name='tarea', null=True, blank=True,
                                   on_delete=models.SET_NULL)

    def get_descripcion_tarea(self):
        descripcion = "%s tiene la factura %s-%s" % (
            self.factura.cliente, self.factura.tipo_documento, self.factura.nro_documento)
        return descripcion


class SeguimientoCartera(TimeStampedModel):
    observacion = models.TextField(max_length=300)
    tarea = models.ForeignKey(TareaCartera, related_name='seguimientos')


# enregion

class TrabajoDia(TimeStampedModel):
    usuario = models.ForeignKey(User)
    nro_tareas = models.PositiveIntegerField(default=0)
    nro_tareas_sin_atender = models.PositiveIntegerField(default=0)
    nro_tareas_atendidas = models.PositiveIntegerField(default=0)
    porcentaje_atendido = models.DecimalField(max_digits=4, decimal_places=1, default=0)

    def __str__(self):
        return "%s - %s" % (self.usuario, self.created.date())

    def get_absolute_url(self):
        return reverse("trabajo_diario:tarea-detail", kwargs={"pk": self.pk})

    def set_actualizar_seguimiento_trabajo(self):
        self.nro_tareas = int(self.mis_tareas.aggregate(Count('id'))['id__count'])
        self.nro_tareas_sin_atender = int(self.mis_tareas.filter(estado=0).aggregate(Count('id'))['id__count'])
        self.nro_tareas_atendidas = self.nro_tareas - self.nro_tareas_sin_atender
        self.porcentaje_atendido = 0
        if self.nro_tareas > 0:
            self.porcentaje_atendido = (self.nro_tareas_atendidas / self.nro_tareas) * 100
        self.save()

    class Meta:
        permissions = (
            ('ver_trabajo_diario', 'Ver Trabajo Diario'),
        )


class TareaDiaria(TimeStampedModel):
    ESTADOS = (
        (0, 'Pendiente'),
        (1, 'Atendida en Proceso'),
        (2, 'Atendida Terminada'),
    )
    mi_dia = models.ForeignKey(TrabajoDia, on_delete=models.CASCADE, related_name='mis_tareas')
    tipo = models.CharField(max_length=120)
    descripcion = models.TextField(max_length=300, null=True, blank=True)
    observacion = models.TextField(max_length=300, null=True, blank=True)
    estado = models.PositiveIntegerField(choices=ESTADOS, default=0)
    url = models.URLField(max_length=300, null=True, blank=True, editable=False)


def set_actualizar_mi_trabajo_diario(sender, instance, created, **kwargs):
    if not created:
        trabajo_dia = instance.mi_dia
        trabajo_dia.set_actualizar_seguimiento_trabajo()


post_save.connect(set_actualizar_mi_trabajo_diario, sender=TareaDiaria)
