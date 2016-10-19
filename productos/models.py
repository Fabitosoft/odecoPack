import math
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from proveedores.models import MargenProvedor
from utils.models import TimeStampedModel


# Create your models here.

# region Categorias Producto
class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    nomenclatura = models.CharField(max_length=3, unique=True)

    class Meta:
        verbose_name_plural = "Categorías Productos"
        verbose_name = "Categoría Producto"

    def __str__(self):
        return self.nombre


# endregion

# region Colores Producto
class ColorProducto(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    nomenclatura = models.CharField(max_length=2, unique=True)

    class Meta:
        verbose_name_plural = "Colores Productos"
        verbose_name = "Color Producto"

    def __str__(self):
        return self.nombre


# endregion

# region Materiales Producto
class MaterialProducto(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    nomenclatura = models.CharField(max_length=2, unique=True)

    class Meta:
        verbose_name_plural = "Materiales Productos"
        verbose_name = "Material Producto"

    def __str__(self):
        return self.nombre


# endregion

# region Series Producto
class SerieProducto(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    nomenclatura = models.CharField(max_length=6, unique=True)

    class Meta:
        verbose_name_plural = "Series Productos"
        verbose_name = "Serie Producto"

    def __str__(self):
        return self.nombre


# endregion

#  region Fabricante Producto
class FabricanteProducto(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    nomenclatura = models.CharField(max_length=2, unique=True)

    class Meta:
        verbose_name_plural = "Fabricantes Productos"
        verbose_name = "Fabricante Producto"

    def __str__(self):
        return self.nombre


# endregion

# region Unidades de Medida
class UnidadMedida(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    nomenclatura = models.CharField(max_length=2, unique=True)

    class Meta:
        verbose_name_plural = "Unidades de Medida"

    def __str__(self):
        return self.nombre


# endregion

# region Productos
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
    con_nombre_automatico = models.BooleanField(default=False, verbose_name='nombre automático')
    fabricante = models.ForeignKey(FabricanteProducto, verbose_name='fabricante', related_name='mis_productos',
                                   on_delete=models.PROTECT)
    serie = models.ForeignKey(SerieProducto, verbose_name='serie', related_name='mis_productos',
                              on_delete=models.PROTECT, default=1)

    # region Caracteristica Físicas Producto
    categoria = models.ForeignKey(CategoriaProducto, verbose_name='categoría', related_name='mis_productos',
                                  on_delete=models.PROTECT)
    categoria_dos = models.CharField(max_length=120, verbose_name='categoría dos')
    tipo = models.CharField(max_length=120, verbose_name='tipo', default='N.A')
    material = models.ForeignKey(MaterialProducto, verbose_name='material', related_name='mis_productos',
                                 on_delete=models.PROTECT, default=1)
    color = models.ForeignKey(ColorProducto, verbose_name='color', related_name='mis_productos',
                              on_delete=models.PROTECT, default=1)
    ancho = models.CharField(max_length=120, verbose_name='ancho (mm)', default='N.A')
    alto = models.CharField(max_length=120, verbose_name='alto (mm)', default='N.A')
    longitud = models.CharField(max_length=120, verbose_name='longitud (mt)', default='N.A')
    diametro = models.CharField(max_length=120, verbose_name='longitud (mm)', default='N.A')
    # endregion

    cantidad_empaque = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT, null=True)
    cantidad_minima_venta = models.DecimalField(max_digits=18, decimal_places=4, default=0)

    margen = models.ForeignKey(MargenProvedor, null=True, blank=True, related_name="productos_con_margen",
                               verbose_name="Id MxC")
    costo = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    costo_cop = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    precio_base = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    rentabilidad = models.DecimalField(max_digits=18, decimal_places=4, default=0)

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

    class Meta:
        verbose_name_plural = "Productos"

    def __init__(self, *args, **kwargs):
        super(Producto, self).__init__(*args, **kwargs)
        self.precio_base_original = self.precio_base
        self.costo_original = self.costo

    def __str__(self):
        return "%s" % (self.descripcion_estandar)

    def save(self, **kwargs):

        margen = kwargs.get("margen_deseado")
        factor_importacion = kwargs.get("factor_importacion")
        tasa = kwargs.get("tasa")

        if not tasa and not factor_importacion and not margen and self.costo != self.costo_original:
            print("en save Cambio Costo")
            self.set_precio_base_y_costo()
        if tasa or factor_importacion or margen:
            print("en save cambio otros")
            self.set_precio_base_y_costo(tasa=tasa, factor_importacion=factor_importacion, margen=margen)

        super().save()

    def set_precio_base_y_costo(self, tasa=None, factor_importacion=None, margen=None):

        if not tasa:
            print("Entro a buscar la tasa")
            tasa = self.margen.proveedor.moneda.moneda_cambio.cambio
        if not factor_importacion:
            print("Entro a buscar el factor")
            factor_importacion = self.margen.proveedor.factor_importacion
        if not margen:
            print("Entro a buscar el margen")
            margen = self.margen.margen_deseado
        margen = (margen) / 100  # Se transforma en porcentaje

        # Calculamos los nuevos costos y precios basados en el cambio de los parametros
        costo_base_cop = self.costo * tasa * factor_importacion
        self.costo_cop = costo_base_cop

        precio_base = costo_base_cop * (1 / (1 - margen))
        self.precio_base = round(precio_base, 4)

        self.rentabilidad = precio_base - costo_base_cop

    def get_nombre_automático(self, tipo):
        if self.con_nombre_automatico:
            nombre = ''
            configuracion = self.categoria.mi_configuracion_producto_nombre_estandar

            if configuracion.con_categoría_uno:
                nombre += self.categoria.nombre

            if configuracion.con_categoría_dos:
                nombre += self.categoria_dos

            if tipo == 'estandar':
                if configuracion.con_fabricante:
                    nombre += self.fabricante.nombre

            if configuracion.con_tipo and self.tipo != 'N.A':
                nombre += self.tipo

            if configuracion.con_material and self.material.id != 1:
                nombre += self.material.nombre

            if configuracion.con_color and self.color.id != 1:
                nombre += self.color.nombre

            if configuracion.con_serie and self.serie.id != 1:
                nombre += self.serie.nombre

            if configuracion.con_ancho and self.ancho != 'N.A':
                nombre += self.ancho

            if configuracion.con_alto and self.alto != 'N.A':
                nombre += self.alto

            if configuracion.con_longitud and self.longitud != 'N.A':
                nombre += self.longitud

            if configuracion.con_diametro and self.diametro != 'N.A':
                nombre += self.diametro

            if tipo == 'comercial':
                self.descripcion_comercial = nombre

            if tipo == 'estandar':
                self.descripcion_estandar = nombre


@receiver(post_save, sender=Producto)
def post_save_producto(sender, instance, *args, **kwargs):
    print('post_save')
    if instance.precio_base_original != instance.precio_base:
        print("Entro a cambiar ensamblado")
        for ensamble in instance.ensamblados.all():
            ensamble.actualizar_precio_total_linea()


# @receiver(post_delete, sender=Producto)
# def post_delete_producto(sender, instance, *args, **kwargs):
#     print('post_delete')
#     if instance.precio_base_original != instance.precio_base:
#         print("Entro a cambiar ensamblado")
#         for ensamble in instance.ensamblados.all():
#             ensamble.actualizar_precio_total_linea()

# endregion

# region Nombre Estandar
class ProductoNombreConfiguracion(models.Model):
    categoria = models.OneToOneField(CategoriaProducto, on_delete=models.CASCADE, verbose_name='categoría',
                                     related_name='mi_configuracion_producto_nombre_estandar', unique=True)
    con_categoría_uno = models.BooleanField(default=True)
    con_categoría_dos = models.BooleanField(default=True)
    con_serie = models.BooleanField(default=True)
    con_fabricante = models.BooleanField(default=False)
    con_tipo = models.BooleanField(default=True)
    con_material = models.BooleanField(default=True)
    con_color = models.BooleanField(default=True)
    con_ancho = models.BooleanField(default=False)
    con_alto = models.BooleanField(default=False)
    con_longitud = models.BooleanField(default=False)
    con_diametro = models.BooleanField(default=False)

    def __str__(self):
        return self.categoria.nombre

    class Meta:
        verbose_name_plural = 'Configuración Nombres Automáticos'
        verbose_name_plural = 'Configuración Nombre Automático'

# endregion
