from django.db.models.signals import post_save, post_delete, pre_delete, pre_init, post_init
from django.dispatch import receiver

from seguimientos.models import SeguimientoComercialCliente
from .models import (
    ComentarioCotizacion,
    ItemCotizacion,
    ImagenCotizacion
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


@receiver(pre_delete, sender=ImagenCotizacion)
def imagen_cotitazion_pre_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.imagen.delete(False)


@receiver(post_init, sender=ImagenCotizacion)
def backup_imagen_cotitazion_imagen_path(sender, instance, **kwargs):
    instance._current_imagen = instance.imagen


@receiver(post_save, sender=ImagenCotizacion)
def delete_imagen_cotitazion_imagen(sender, instance, **kwargs):
    if hasattr(instance, '_current_imagen'):
        if instance._current_imagen != instance.imagen:
            instance._current_imagen.delete(save=False)
