from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

from proveedores.models import MargenProvedor
from utils.models import TimeStampedModel


# Create your models here.

######################################################################################################################
# UNIDADES DE MEDIDA
######################################################################################################################
class UnidadMedida(models.Model):
    nombre = models.CharField(max_length=120, unique=True)

    class Meta:
        verbose_name_plural = "unidades de medida"

    def __str__(self):
        return self.nombre


######################################################################################################################
# PRODUCTOS
######################################################################################################################
def productos_upload_to(instance, filename):
    basename, file_extention = filename.split(".")
    new_filename = "produ_perfil_%s.%s" % (basename, file_extention)
    return "%s/%s/%s" % ("productos", "foto_perfil", new_filename)


class ProductoQuerySet(models.QuerySet):
    def para_ensamble(self):
        return self.filter(activo_ensamble=True)

    def para_catalogo(self):
        return self.filter(activo_catalogo=True)

    def para_componentes(self):
        return self.filter(activo_componentes=True)

    def para_proyectos(self):
        return self.filter(activo_proyectos=True)
        #
        # def editors(self):
        #     return self.filter(role='E')


class ProductoActivosManager(models.Manager):
    def get_queryset(self):
        return ProductoQuerySet(self.model, using=self._db).filter(activo=True)

    def modulos(self):
        return self.get_queryset().para_ensamble()

    def catalogo(self):
        return self.get_queryset().para_catalogo()

    def componentes(self):
        return self.get_queryset().para_componentes()

    def proyectos(self):
        return self.get_queryset().para_proyectos()


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
    cantidad_empaque = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT, null=True)
    cantidad_minima_venta = models.DecimalField(max_digits=18, decimal_places=4, default=0)

    margen = models.ForeignKey(MargenProvedor, null=True, blank=True, related_name="productos_con_margen",
                               verbose_name="Id MxC")
    costo = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    costo_cop = models.DecimalField(max_digits=18, decimal_places=4, default=0)

    precio_base = models.DecimalField(max_digits=18, decimal_places=4, default=0)

    activo = models.BooleanField(default=True)
    activo_componentes = models.BooleanField(default=True, verbose_name="En Compo.")
    activo_proyectos = models.BooleanField(default=True, verbose_name="En Proy.")
    activo_catalogo = models.BooleanField(default=True, verbose_name="En Cata.")
    activo_ensamble = models.BooleanField(default=False, verbose_name="Para Ensam.")

    foto_perfil = models.ImageField(upload_to=productos_upload_to, validators=[validate_image], null=True, blank=True)
    created_by = models.ForeignKey(User, editable=False, null=True, blank=True, related_name="servicio_created")
    updated_by = models.ForeignKey(User, editable=False, null=True, blank=True, related_name="servicio_updated")

    objects = models.Manager()
    activos = ProductoActivosManager()

    def save(self):
        self.set_precio_base_y_costo()
        super().save()
        for ensamble in self.ensamblados.all():
            ensamble.save()

    def __str__(self):
        return "%s" % (self.descripcion_estandar)

    def set_precio_base_y_costo(self):
        self.costo_cop = self.costo * (
            self.margen.proveedor.moneda.moneda_cambio.cambio) * (self.margen.proveedor.factor_importacion)

        self.precio_base = self.costo * (1 + self.margen.margen_deseado / 100) * (
            self.margen.proveedor.moneda.moneda_cambio.cambio) * (self.margen.proveedor.factor_importacion)
