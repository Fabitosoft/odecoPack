from django.contrib.auth.models import User
from django.db import models

from model_utils.models import TimeStampedModel, SoftDeletableModel

from biable.models import Cliente
from geografia_colombia.models import Ciudad


# Create your models here.

class ContactoCargo(TimeStampedModel):
    cargo = models.CharField(max_length=60, unique=True)


class ContactoEmpresa(TimeStampedModel):
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    correo_electronico = models.EmailField(null=True, blank=True)
    correo_electronico_alternativo = models.EmailField(null=True, blank=True)
    nro_telefonico = models.CharField(max_length=120)
    nro_telefonico_alternativo = models.CharField(max_length=120)
    cliente = models.ForeignKey(Cliente, blank=True, null=True, related_name='mis_contactos')
    ciudad = models.ForeignKey(Ciudad, blank=True, null=True, related_name='mis_contactos')
    ciudad_alternativa = models.CharField(max_length=120, blank=True, null=True)
    empresa_alternativa = models.CharField(max_length=120, blank=True, null=True)
    nit_alternativo = models.CharField(max_length=120, blank=True, null=True)
    creado_por = models.ForeignKey(User, related_name='mis_contactos')
    retirado = models.BooleanField(default=False)
    cargo = models.ForeignKey(ContactoCargo, related_name='mis_contactos')

    class Meta:
        verbose_name_plural = 'Contactos Empresas'
        verbose_name = 'Contacto Empresa'
