from decimal import Decimal

from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from model_utils.models import TimeStampedModel

from .managers import BandaActivasQuerySet
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

def imagen_ensamblado_banda_upload_to(instance, filename):
    fecha_hoy = timezone.now().strftime('%Y%m%d%H%M%S')
    print(fecha_hoy)
    basename, file_extention = filename.split(".")
    new_filename = "ensamblado_%s.%s" % (fecha_hoy, file_extention)
    return "%s/%s/%s" % ("bandas", "ensamblado", new_filename)


class Banda(TimeStampedModel):
    """
    Genera un ensamblaje de banda
    **Context**
    ``banda`` An instance of :model:`bandas.banda`.

    """
    # region Caracteristicas Comunes
    id_cguno = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to=imagen_ensamblado_banda_upload_to, null=True, blank=True)
    descripcion_estandar = models.CharField(max_length=200, default='AUTOMÁTICO')
    descripcion_comercial = models.CharField(max_length=200, default='AUTOMÁTICO')
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
    con_torneado_varilla = models.BooleanField(default=False)
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
    costo_ensamblado = models.ForeignKey('CostoEnsambladoBlanda', null=True, editable=False, related_name='mis_bandas')
    con_nombre_automatico = models.BooleanField(default=True, verbose_name='nombre automático')

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

    def save(self):
        self.costo_ensamblado = CostoEnsambladoBlanda.objects.filter(aleta=self.con_aleta,
                                                                     empujador=self.con_empujador,
                                                                     torneado=self.con_torneado_varilla).first()
        super().save()

    def get_costo_cop(self):
        modulos = self.ensamblado.select_related(
            'producto',
            'producto__margen__proveedor',
            'producto__margen__proveedor__moneda',
        ).all()
        if modulos:
            costo = 0
            for modulo in modulos:
                costo += modulo.get_costo_cop_linea()
            return costo
        return 0

    def get_precio_base(self):
        modulos = self.ensamblado.select_related(
            'producto',
            'producto__margen__proveedor',
            'producto__margen__proveedor__moneda',
        ).all()
        if modulos:
            precio = 0
            for modulo in modulos:
                precio += modulo.get_precio_base_linea()
            return precio
        return 0

    def get_precio_mano_obra(self):
        if self.costo_ensamblado:
            self.costo_mano_obra = (self.costo_ensamblado.porcentaje / 100) * self.get_precio_base()
        return self.costo_mano_obra

    def get_precio_con_mano_obra(self):
        return self.get_precio_mano_obra() + self.get_precio_base()

    objects = models.Manager()
    activos = BandaActivasQuerySet.as_manager()

    ensamblaje = models.ManyToManyField(
        Producto,
        through='Ensamblado',
        through_fields=('banda', 'producto'),
    )

    class Meta:
        verbose_name_plural = '3. Bandas'
        verbose_name = '3. Banda'

    def get_absolute_url(self):
        return reverse("bandas:detalle_banda", kwargs={"pk": self.pk})

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

        if self.con_nombre_automatico:
            self.descripcion_estandar = self.referencia
            self.descripcion_comercial = nombre.strip().title()

    def __str__(self):
        return self.referencia


# endregion

# region Ensamblado
class Ensamblado(TimeStampedModel):
    banda = models.ForeignKey(Banda, on_delete=models.CASCADE, related_name='ensamblado')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='ensamblados')

    cortado_a = models.CharField(max_length=10, verbose_name="Cortado a", default="COMPLETA")
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad")
    created_by = models.ForeignKey(User, editable=False, null=True, blank=True, related_name="ensamblado_created_by")
    updated_by = models.ForeignKey(User, editable=False, null=True, blank=True, related_name="ensamblado_updated_by")

    class Meta:
        verbose_name_plural = '2. Ensamblados'
        verbose_name = '2. Ensamblado'

    def get_costo_cop_linea(self):
        return round(self.producto.get_costo_cop() * self.cantidad, 0)

    def get_precio_base_linea(self):
        return round(self.producto.get_precio_base() * Decimal(self.cantidad), 0)

    def get_rentabilidad_linea(self):
        return round(self.get_precio_base_linea() - self.get_costo_cop_linea(), 0)


# endregion

# region CostoEnsamblado
class CostoEnsambladoBlanda(models.Model):
    nombre = models.CharField(max_length=30)
    aleta = models.BooleanField(default=False)
    empujador = models.BooleanField(default=False)
    torneado = models.BooleanField(default=False)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        verbose_name = '1. Costo Emsamblado'
        verbose_name_plural = '1. Costos Emsamblados'
        unique_together = ('aleta', 'empujador', 'torneado')

# endregion

# endregion
