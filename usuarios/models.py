from django.db import models
from django.contrib.auth.models import User

from empresas.models import Empresa
# Create your models here.

def avatar_upload_to(instance, filename):
    username = instance.user.username
    basename, file_extention = filename.split(".")
    new_filename = "%s_%s.%s" % (username, basename, file_extention)
    return "user/avatar/%s/%s" % (username, new_filename)

class UserExtended(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=1, choices=((('I', 'Colaborador'),('E', 'Cliente'))))
    avatar = models.ImageField(blank=True, upload_to=avatar_upload_to)

    def __str__(self):
        return self.user.first_name


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

