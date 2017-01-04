from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.db import models
from django.contrib.auth.models import User

from empresas.models import Empresa


# Create your models here.

class UserExtended(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_extendido")
    tipo = models.CharField(max_length=1, choices=(('I', 'Colaborador'), ('E', 'Cliente')))

    def __str__(self):
        return self.user.first_name

    def es_colaborador(self):
        return Colaborador.objects.filter(usuario=self).exists()


def colaborador_upload_to(instance, filename):
    basename, file_extention = filename.split(".")
    new_filename = "colaborador_perfil_%s.%s" % (basename, file_extention)
    return "%s/%s/%s/%s/%s" % ("usuarios", instance.usuario.user.id, "foto_perfil", "colaborador", new_filename)


class Colaborador(models.Model):
    def validate_image(fieldfile_obj):
        w, h = get_image_dimensions(fieldfile_obj)
        filesize = fieldfile_obj.file.size
        megabyte_limit = 1
        if filesize > megabyte_limit * 1024 * 1024:
            raise ValidationError("Tamaño Máximo del Archivo es %sMB" % str(megabyte_limit))
        if w > 300 or h > 300:
            raise ValidationError("Tamaño Máximo de la imagen es 300x300")

    usuario = models.OneToOneField(UserExtended, on_delete=models.PROTECT, related_name="colaborador")
    numero_contacto = models.CharField(max_length=12)
    extencion = models.CharField(max_length=10)
    foto_perfil = models.ImageField(upload_to=colaborador_upload_to, validators=[validate_image], null=True, blank=True)
    subalternos = models.ManyToManyField("self", blank=True)


    class Meta:
        verbose_name_plural = "colaboradores"

    def __str__(self):
        return self.usuario.user.get_full_name()


class ClienteEmpresa(models.Model):
    usuario = models.OneToOneField(UserExtended, on_delete=models.PROTECT, related_name="cliente_empresa")
    empresa = models.OneToOneField(Empresa, related_name="perfil_cliente", null=True)

    class Meta:
        verbose_name_plural = "empresas"

    def __str__(self):
        return self.empresa.nombre