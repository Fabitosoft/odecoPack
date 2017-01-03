from django.db import models
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions

from imagekit.models import ImageSpecField
from model_utils.models import TimeStampedModel
from pilkit.processors import ResizeToFill

from biable.models import Cliente


# Create your models here.
class TipoDocumento(models.Model):
    nombre = models.CharField(max_length=100)
    nomenclatura = models.CharField(max_length=2)


class Transaccion(TimeStampedModel):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='mis_transacciones', null=True,
                                blank=True)
    descripcion = models.TextField(max_length=300)


class Documento(TimeStampedModel):
    tipo = models.ForeignKey(TipoDocumento, on_delete=models.PROTECT, related_name='mis_documentos')
    transaccion = models.ForeignKey(Transaccion, on_delete=models.PROTECT, related_name='mis_documentos')


class ImagenDocumento(TimeStampedModel):
    def validate_image(fieldfile_obj):
        w, h = get_image_dimensions(fieldfile_obj)
        filesize = fieldfile_obj.file.size
        megabyte_limit = 2
        if filesize > megabyte_limit * 1024 * 1024:
            raise ValidationError("Tamaño Máximo del Archivo es %sMB" % str(megabyte_limit))
        if w > 1024 or h > 800:
            raise ValidationError("Tamaño Máximo de la imagen es 1024x800")

    documento = models.ForeignKey(Documento, on_delete=models.PROTECT, related_name='mis_imagenes')
    imagen = models.ImageField(upload_to='documentos/digitalizacion/imagenes', validators=[validate_image])
    imagen_thumbnail = ImageSpecField(source='imagen',
                                      processors=[ResizeToFill(100, 50)],
                                      format='PNG',
                                      options={'quality': 60})