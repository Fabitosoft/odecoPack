from decimal import Decimal
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.urls import reverse

from utils.models import TimeStampedModel
from productos.models import Producto

from productos_caracteristicas.models import (
    MaterialProducto,
    ColorProducto,
    FabricanteProducto,
    SerieProducto
)

from productos_categorias.models import (
    TipoProductoCategoría
)


# Create your models here.


# region Ensamblaje Bandas

# region Banda
class BandaQuerySet(models.QuerySet):
    def para_catalogo(self):
        return self.filter(activo_catalogo=True)

    def para_componentes(self):
        return self.filter(activo_componentes=True)

    def para_proyectos(self):
        return self.filter(activo_proyectos=True)


class BandaActivosManager(models.Manager):
    def get_queryset(self):
        return BandaQuerySet(self.model, using=self._db).filter(activo=True)

    def catalogo(self):
        return self.get_queryset().para_catalogo()

    def componentes(self):
        return self.get_queryset().para_componentes()

    def proyectos(self):
        return self.get_queryset().para_proyectos()


class Banda(TimeStampedModel):
    """
    Genera un ensamblaje de banda
    **Context**
    ``banda`` An instance of :model:`bandas.banda`.

    """
    # region Caracteristicas Comunes
    id_cguno = models.PositiveIntegerField(default=0)
    descripcion_estandar = models.CharField(max_length=200)
    descripcion_comercial = models.CharField(max_length=200)
    referencia = models.CharField(max_length=120, unique=True, null=True, blank=True)
    fabricante = models.ForeignKey(FabricanteProducto, related_name="bandas_con_fabricante")  # fabricante
    # endregion

    # region Caracteristicas Básicas de Banda
    serie = models.ForeignKey(SerieProducto, related_name="bandas_con_serie")  # series
    paso = models.PositiveIntegerField(default=0)
    tipo = models.ForeignKey(TipoProductoCategoría, related_name="bandas_con_tipo")  # tipo
    material = models.ForeignKey(MaterialProducto, related_name="bandas_con_material")  # materiales
    color = models.ForeignKey(ColorProducto, related_name="bandas_con_color")  # colores
    ancho = models.PositiveIntegerField(default=0, verbose_name="Ancho (mm)")
    longitud = models.DecimalField(decimal_places=2, max_digits=8, default=1, verbose_name="Longitud (m)")
    material_varilla = models.ForeignKey(MaterialProducto, related_name="bandas_con_material_varilla")  # materiales
    total_filas = models.PositiveIntegerField(default=0)
    # endregion

    # region Empujadores
    con_empujador = models.BooleanField(default=False)
    empujador_tipo = models.ForeignKey(TipoProductoCategoría, null=True, blank=True,
                                       related_name="bandas_con_tipo_empujador", verbose_name="Tipo")  # tipo
    empujador_altura = models.PositiveIntegerField(default=0, verbose_name="Altura (mm)")
    empujador_ancho = models.PositiveIntegerField(default=0, verbose_name="Ancho (mm)")
    empujador_distanciado = models.PositiveIntegerField(default=0, null=True, blank=True,
                                                        verbose_name="Distanciado (mm)")
    empujador_identacion = models.CharField(max_length=10, default="N.A", verbose_name="Identacion")

    empujador_filas_entre = models.PositiveIntegerField(null=True, blank=True, verbose_name="Filas entre Empujador")
    empujador_total_filas = models.PositiveIntegerField(null=True, blank=True, verbose_name="Total Filas Empujador")

    # endregion

    # region Aleta
    con_aleta = models.BooleanField(default=False)
    aleta_altura = models.PositiveIntegerField(default=0, verbose_name="Altura (mm)")
    aleta_identacion = models.CharField(max_length=10, default="N.A", verbose_name="Identacion")

    # endregion

    created_by = models.ForeignKey(User, editable=False, null=True, blank=True, related_name="banda_created_by")
    updated_by = models.ForeignKey(User, editable=False, null=True, blank=True, related_name="banda_updated_by")

    class Meta:
        permissions = (
            ('full_bandas', 'Full Bandas'),
        )

    # region Atributos de activación
    activo = models.BooleanField(default=False, verbose_name="Activo")
    activo_componentes = models.BooleanField(default=False, verbose_name="En Compo.")
    activo_proyectos = models.BooleanField(default=False, verbose_name="En Proy.")
    activo_catalogo = models.BooleanField(default=False, verbose_name="En Cata.")
    # endregion

    # region Precios y Costos
    precio_banda = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    precio_total = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    costo_base_total = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    rentabilidad = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    costo_mano_obra = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    # endregion

    objects = models.Manager()
    activos = BandaActivosManager()

    ensamblaje = models.ManyToManyField(
        Producto,
        through='Ensamblado',
        through_fields=('banda', 'producto'),
    )

    class Meta:
        verbose_name_plural = '3. Bandas'
        verbose_name = '3. Banda'

    def save(self):
        modulos = self.ensamblado.all()
        costo_ensamblado = CostoEnsambladoBlanda.objects.filter(aleta=self.con_aleta,
                                                                empujador=self.con_empujador).first()
        porcentaje_mano_obra = 0
        if costo_ensamblado:
            porcentaje_mano_obra = costo_ensamblado.porcentaje / 100

        if modulos:
            print('Entro a actualizar precio banda')
            precio = modulos.aggregate(precio=Sum('precio_linea'))['precio']
            self.precio_banda = precio
            costo_base = modulos.aggregate(costo=Sum('costo_cop_linea'))['costo']
            self.costo_base_total = costo_base
        else:
            self.costo_base_total = 0
            self.precio_banda = 0
            self.precio_total = 0

        self.costo_mano_obra = self.costo_base_total * porcentaje_mano_obra
        self.precio_total = self.precio_banda + self.costo_mano_obra
        self.rentabilidad = self.precio_banda - self.costo_base_total
        super().save()

    def get_absolute_url(self):
        return reverse("bandas:detalle_banda", kwargs={"pk": self.pk})

    def actualizar_precio_total(self):
        self.save()

    def generar_referencia(self):
        referencia = (
                         "%s"
                         "%s-"
                         "%s"
                         "%s"
                         "%s"
                         "%s"
                         "V%s"
                         "W%s"
                     ) % \
                     (
                         "B",
                         self.fabricante.nomenclatura,
                         self.serie.nomenclatura,
                         self.tipo.tipo.nomenclatura,
                         self.material.nomenclatura,
                         self.color.nomenclatura,
                         self.material_varilla.nomenclatura,
                         self.ancho,
                     )

        nombre = (
                     "%s"
                     " %s"
                     " %s"
                     " %s"
                     " %s"
                     " %s"
                     " V%s"
                     " W%s"
                 ) % \
                 (
                     "Banda",
                     self.fabricante.nombre,
                     self.serie.nombre,
                     self.tipo.tipo.nombre,
                     self.material.nombre,
                     self.color.nombre,
                     self.material_varilla.nombre,
                     self.ancho,
                 )

        if self.con_empujador:
            referencia += (
                              "/%s"
                              "%s"
                              "H%s"
                              "W%s"
                              "D%s"
                              "I%s"
                          ) % \
                          (
                              "E",
                              self.empujador_tipo.tipo.nomenclatura,
                              self.empujador_altura,
                              self.empujador_ancho,
                              self.empujador_distanciado,
                              self.empujador_identacion,
                          )
            nombre += (
                              " %s"
                              " %s"
                              " H%s"
                              " W%s"
                              " D%s"
                              " I%s"
                          ) % \
                          (
                              "con Empujador",
                              self.empujador_tipo.tipo.nombre,
                              self.empujador_altura,
                              self.empujador_ancho,
                              self.empujador_distanciado,
                              self.empujador_identacion,
                          )
        if self.con_aleta:
            referencia += (
                              "/%s"
                              "H%s"
                              "I%s"
                          ) % \
                          (
                              "A",
                              self.aleta_altura,
                              self.aleta_identacion,
                          )

            nombre += (
                              " %s"
                              " H%s"
                              " I%s"
                          ) % \
                          (
                              "con Aleta",
                              self.aleta_altura,
                              self.aleta_identacion,
                          )

        self.referencia = referencia.upper()
        self.descripcion_comercial = nombre.strip().title()
        self.descripcion_estandar = self.referencia

    def __str__(self):
        return self.referencia


# endregion

# region Ensamblado
class Ensamblado(TimeStampedModel):
    banda = models.ForeignKey(Banda, on_delete=models.CASCADE, related_name='ensamblado')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='ensamblados')

    precio_linea = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    costo_cop_linea = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    rentabilidad = models.DecimalField(max_digits=18, decimal_places=4, default=0)

    cortado_a = models.CharField(max_length=10, verbose_name="Cortado a")
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad")
    created_by = models.ForeignKey(User, editable=False, null=True, blank=True, related_name="ensamblado_created_by")
    updated_by = models.ForeignKey(User, editable=False, null=True, blank=True, related_name="ensamblado_updated_by")

    class Meta:
        verbose_name_plural = '2. Ensamblados'
        verbose_name = '2. Ensamblado'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.precio_linea_original = self.precio_linea
        self.cantidad_original = self.cantidad

    def save(self):
        self.precio_linea = Decimal(self.producto.precio_base) * Decimal(self.cantidad)
        self.costo_cop_linea = Decimal(self.producto.costo_cop) * Decimal(self.cantidad)
        self.rentabilidad = self.precio_linea - self.costo_cop_linea
        super().save()

    def actualizar_precio_total_linea(self):
        self.save()


@receiver(post_save, sender=Ensamblado)
def post_save_ensamblado(sender, instance, *args, **kwargs):
    instance.banda.actualizar_precio_total()


@receiver(post_delete, sender=Ensamblado)
def post_delete_ensamblado(sender, instance, *args, **kwargs):
    instance.banda.actualizar_precio_total()


# endregion

# region CostoEnsamblado
class CostoEnsambladoBlanda(models.Model):
    nombre = models.CharField(max_length=30)
    aleta = models.BooleanField(default=False)
    empujador = models.BooleanField(default=False)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        verbose_name = '1. Costo Emsamblado'
        verbose_name_plural = '1. Costos Emsamblados'
        unique_together = ('aleta', 'empujador')

# endregion

# endregion
