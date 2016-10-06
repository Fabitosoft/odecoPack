from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


from utils.models import TimeStampedModel

# Create your models here.
class UnidadMedida(models.Model):
    nombre = models.CharField(max_length=120, unique=True)

    class Meta:
        verbose_name_plural = "unidades de medida"

    def __str__(self):
        return self.nombre

def productos_upload_to(instance, filename):
    basename, file_extention = filename.split(".")
    new_filename = "produ_perfil_%s.%s" % (basename, file_extention)
    return "%s/%s/%s" % ("productos","foto_perfil", new_filename)

class Producto(TimeStampedModel):
    def validate_image(fieldfile_obj):
        filesize = fieldfile_obj.file.size
        megabyte_limit = 1.0
        if filesize > megabyte_limit * 1024 * 1024:
            raise ValidationError("Max file size is %sMB" % str(megabyte_limit))

    id_cguno = models.PositiveIntegerField(default=0)
    referencia = models.CharField(max_length=120, unique=True)
    descripcion_estandar = models.CharField(max_length=200)
    descripcion_comercial = models.CharField(max_length=200)
    serie = models.CharField(max_length=10, default="")
    fabricante = models.CharField(max_length=60, null=True, blank=True)
    cantidad_empaque = models.DecimalField(max_digits=10,decimal_places=4, default=0)
    unidad_medida = models.ForeignKey(UnidadMedida,on_delete=models.PROTECT, null=True)
    cantidad_minima_venta = models.DecimalField(max_digits=10,decimal_places=4, default=0)
    activo = models.BooleanField(default=True)
    activo_componentes = models.BooleanField(default=True)
    activo_proyectos = models.BooleanField(default=True)
    activo_catalogo = models.BooleanField(default=True)
    activo_ensamble = models.BooleanField(default=True)
    foto_perfil = models.ImageField(upload_to=productos_upload_to, validators=[validate_image], null=True, blank=True)
    created_by = models.ForeignKey(User, editable=False, null=True, blank=True, related_name="servicio_created")
    updated_by = models.ForeignKey(User, editable=False, null=True, blank=True, related_name="servicio_updated")

    def __str__(self):
        return self.referencia
