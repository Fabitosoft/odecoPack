from django.db.models.signals import pre_delete, post_init, post_save
from django.dispatch import receiver

from .models import Banda


@receiver(pre_delete, sender=Banda)
def imagen_banda_pre_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.imagen.delete(False)


@receiver(post_init, sender=Banda)
def backup_imagen_banda_path(sender, instance, **kwargs):
    instance._current_imagen = instance.imagen


@receiver(post_save, sender=Banda)
def delete_imagen_banda(sender, instance, **kwargs):
    if hasattr(instance, '_current_imagen'):
        if instance._current_imagen != instance.imagen:
            instance._current_imagen.delete(save=False)
