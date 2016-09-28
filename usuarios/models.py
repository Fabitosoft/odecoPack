from django.db import models
from django.contrib.auth.models import User

from empresas.models import Empresa
# Create your models here.

class UserExtended(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_extendido")
    tipo = models.CharField(max_length=1, choices=((('I', 'Colaborador'),('E', 'Cliente'))))


    def __str__(self):
        return self.user.first_name

    def es_vendedor(self):
        return Vendedor.objects.filter(usuario=self).exists()


class Vendedor(models.Model):
    usuario = models.OneToOneField(UserExtended, on_delete=models.PROTECT, related_name="vendedor")

    class Meta:
        verbose_name_plural = "vendedores"

    def __str__(self):
        return self.usuario.user.get_full_name()


class ClienteEmpresa(models.Model):
    usuario = models.OneToOneField(UserExtended, on_delete=models.PROTECT, related_name="cliente_empresa")
    empresa = models.OneToOneField(Empresa, related_name="perfil_cliente", null=True)

    class Meta:
        verbose_name_plural = "empresas"

    def __str__(self):
        return self.empresa.nombre

