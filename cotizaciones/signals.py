from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from seguimientos.models import SeguimientoComercialCliente
from .models import (
    ComentarioCotizacion,
    ItemCotizacion
)


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


@receiver([post_save, post_delete], sender=ItemCotizacion)
def cotizacion_item_post_save_receiver(sender, instance, *args, **kwargs):
    instance.cotizacion.update_total()
