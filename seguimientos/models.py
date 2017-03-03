from django.contrib.auth.models import User
from django.db import models

from model_utils.models import TimeStampedModel

from biable.models import Cliente, SeguimientoCliente
from contactos.models import ContactoEmpresa
from cotizaciones.models import Cotizacion, ComentarioCotizacion
from trabajo_diario.models import SeguimientoCartera, SeguimientoCotizacion, SeguimientoEnvioTCC


# Create your models here.
class SeguimientoComercialCliente(TimeStampedModel):
    cliente = models.ForeignKey(Cliente, related_name='mi_seguimiento_comercial')
    creado_por = models.ForeignKey(User, related_name='mi_seguimiento_comercial', null=True, blank=True)
    observacion_adicional = models.TextField()
    tipo_accion = models.CharField(max_length=120)
    contacto = models.ForeignKey(ContactoEmpresa, null=True, blank=False)
    seguimiento_cliente = models.ForeignKey(SeguimientoCliente, null=True, blank=False)
    cotizacion = models.ForeignKey(Cotizacion, null=True, blank=False)
    comentario_cotizacion = models.ForeignKey(ComentarioCotizacion, null=True, blank=False)
    seguimiento_cartera = models.ForeignKey(SeguimientoCartera, null=True, blank=False)
    seguimiento_cotizacion = models.ForeignKey(SeguimientoCotizacion, null=True, blank=False)
    seguimiento_envio_tcc = models.ForeignKey(SeguimientoEnvioTCC, null=True, blank=False)

    def get_descripcion(self):
        if self.contacto:
            return None
        elif self.seguimiento_cliente:
            return None
        elif self.cotizacion:
            return None
        elif self.comentario_cotizacion:
            return None
        elif self.seguimiento_cartera:
            return None
        elif self.seguimiento_cotizacion:
            return None
        elif self.seguimiento_envio_tcc:
            return None
