from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from seguimientos.models import SeguimientoComercialCliente
from .models import ContactoEmpresa


@receiver(post_save, sender=ContactoEmpresa)
def crear_seguimiento_comercial_contacto(sender, instance, created, **kwargs):
    seguimiento = SeguimientoComercialCliente()
    seguimiento.contacto = instance
    seguimiento.creado_por = instance.creado_por
    seguimiento.cliente = instance.cliente
    observacion_adicional = "<ul>"
    if created:
        seguimiento.tipo_accion = "Creó"
    else:
        seguimiento.tipo_accion = "Actualizó"

    for k, v in instance.__dict__.items():
        if v and k[0] != '_' and 'id' not in k and 'modified' not in k and 'created' not in k:
            atributo = "<li>%s: %s</li>" % (k.replace('_', ' ').title(), v)
            observacion_adicional += atributo
    observacion_adicional += "</ul>"
    seguimiento.observacion_adicional = observacion_adicional
    seguimiento.save()
