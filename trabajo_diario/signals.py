from django.db.models.signals import post_save
from django.dispatch import receiver

from seguimientos.models import SeguimientoComercialCliente
from .models import SeguimientoCotizacion, SeguimientoEnvioTCC, SeguimientoCartera


@receiver(post_save, sender=SeguimientoCotizacion)
def crear_seguimiento_comercial_seguimiento_tarea_cotizacion(sender, instance, created, **kwargs):
    if instance.tarea.cotizacion.cliente_biable and instance.observacion:
        seguimiento = SeguimientoComercialCliente()
        seguimiento.seguimiento_cotizacion = instance
        seguimiento.creado_por = instance.usuario
        seguimiento.cliente = instance.tarea.cotizacion.cliente_biable
        observacion_adicional = "<p>Estado: " + instance.tarea.get_estado_display() + "</p>"
        observacion_adicional += "<p>" + instance.observacion + "</p>"
        seguimiento.observacion_adicional = observacion_adicional
        if created:
            seguimiento.tipo_accion = "Realizó"
        seguimiento.save()


@receiver(post_save, sender=SeguimientoEnvioTCC)
def crear_seguimiento_comercial_seguimiento_tarea_envio_tcc(sender, instance, created, **kwargs):
    if instance.observacion:
        seguimiento = SeguimientoComercialCliente()
        seguimiento.seguimiento_envio_tcc = instance
        seguimiento.creado_por = instance.usuario
        seguimiento.cliente = instance.tarea.envio.cliente
        observacion_adicional = "<p>Estado: " + instance.tarea.get_estado_display() + "</p>"
        observacion_adicional += "<p>" + instance.observacion + "</p>"
        seguimiento.observacion_adicional = observacion_adicional
        if created:
            seguimiento.tipo_accion = "Realizó"
        seguimiento.save()


@receiver(post_save, sender=SeguimientoCartera)
def crear_seguimiento_comercial_seguimiento_tarea_cartera(sender, instance, created, **kwargs):
    if instance.observacion:
        seguimiento = SeguimientoComercialCliente()
        seguimiento.seguimiento_cartera = instance
        seguimiento.creado_por = instance.usuario
        seguimiento.cliente = instance.tarea.factura.cliente
        observacion_adicional = "<p>Estado: " + instance.tarea.get_estado_display() + "</p>"
        observacion_adicional += "<p>" + instance.observacion + "</p>"
        seguimiento.observacion_adicional = observacion_adicional
        if created:
            seguimiento.tipo_accion = "Realizó"
        seguimiento.save()
