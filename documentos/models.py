from django.db import models
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions

from imagekit.models import ImageSpecField
from model_utils.models import TimeStampedModel
from pilkit.processors import ResizeToFill

from biable.models import Cliente


# Create your models here.
class TipoDocumento(models.Model):
    cliente = models.ForeignKey(Cliente, related_name='mis_documentos', on_delete=models.PROTECT, null=True, blank=True)
    nombre = models.CharField(max_length=100, unique=True)
    nomenclatura = models.CharField(max_length=2, unique=True)

    def __str__(self):
        return self.nombre

class Documento(TimeStampedModel):
    tipo = models.ForeignKey(TipoDocumento, on_delete=models.PROTECT, related_name='mis_documentos', verbose_name='Tipo Documento')
    nro = models.CharField(max_length=10, verbose_name='Nro. Documento')

    class Meta:
        unique_together = ('tipo','nro',)

    def __str__(self):
        return "%s-%s"%(self.tipo,self.nro)


def imagen_documento_upload_to(instance, filename):
    basename, file_extention = filename.split(".")
    documento = instance.documento
    new_filename = "documento_digital_%s_%s.%s" % (documento.tipo, documento.nro, file_extention)
    return "documentos/digitalizacion/imagenes/%s" % new_filename


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
    imagen = models.ImageField(upload_to=imagen_documento_upload_to, validators=[validate_image])
    imagen_thumbnail = ImageSpecField(source='imagen',
                                      processors=[ResizeToFill(100, 50)],
                                      format='PNG',
                                      options={'quality': 60})