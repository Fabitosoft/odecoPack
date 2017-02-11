from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from model_utils.models import TimeStampedModel, SoftDeletableModel

from biable.models import SucursalBiable
from geografia_colombia.models import Ciudad


# Create your models here.


class ContactoEmpresa(TimeStampedModel):
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    correo_electronico = models.EmailField(null=True, blank=True)
    correo_electronico_alternativo = models.EmailField(null=True, blank=True)
    nro_telefonico = models.CharField(max_length=120, null=True, blank=True)
    nro_telefonico_alternativo = models.CharField(max_length=120, null=True, blank=True)
    nro_telefonico_alternativo_dos = models.CharField(max_length=120, null=True, blank=True)
    sucursal = models.ForeignKey(SucursalBiable, blank=True, null=True, related_name='mis_contactos')
    creado_por = models.ForeignKey(User, related_name='mis_contactos', null=True, blank=True)
    retirado = models.BooleanField(default=False)
    cargo = models.CharField(max_length=120, blank=True, null=True)
    fecha_cumpleanos = models.DateField(null=True, blank=True)

    def get_absolute_url(self):
        return reverse("biable:detalle_cliente", kwargs={"pk": self.sucursal.cliente.nit })

    def get_absolute_url_update(self):
        return reverse('contactos:actualizar_contacto_empresa', kwargs={'pk': self.pk})

    class Meta:
        verbose_name_plural = 'Contactos Empresas'
        verbose_name = 'Contacto Empresa'
