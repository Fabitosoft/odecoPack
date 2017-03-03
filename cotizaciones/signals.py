from django.db.models.signals import post_save
from django.dispatch import receiver

from seguimientos.models import SeguimientoComercialCliente
from .models import ComentarioCotizacion, Cotizacion


@receiver(post_save, sender=ComentarioCotizacion)
def crear_seguimiento_comercial_comentario_cotizacion(sender, instance, created, **kwargs):
    if instance.cotizacion.cliente_biable:
        seguimiento = SeguimientoComercialCliente()
        seguimiento.comentario_cotizacion = instance
        seguimiento.creado_por = instance.usuario
        seguimiento.cliente = instance.cotizacion.cliente_biable
        observacion_adicional = "<p>" + instance.comentario + "</p>"
        seguimiento.observacion_adicional = observacion_adicional
        if created:
            seguimiento.tipo_accion = "Comentó"
        seguimiento.save()
