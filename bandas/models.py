from decimal import Decimal
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from utils.models import TimeStampedModel
from productos.models import Producto


# Create your models here.
# region Caracteristicas
class Caracteristica(models.Model):
    nombre = models.CharField(max_length=60)

    def __str__(self):
        return self.nombre


class ValorCaracteristica(models.Model):
    caracteristica = models.ForeignKey(Caracteristica)
    nombre = models.CharField(max_length=60)
    nomenclatura = models.CharField(max_length=6, blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        unique_together=(('caracteristica','nombre'),('caracteristica','nomenclatura'))

    def __str__(self):
        return self.nombre


# endregion

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
    fabricante = models.ForeignKey(ValorCaracteristica, related_name="bandas_con_fabricante")
    # endregion

    # region Caracteristicas Básicas de Banda
    serie = models.ForeignKey(ValorCaracteristica, related_name="bandas_con_serie")
    paso = models.PositiveIntegerField(default=0)
    tipo = models.ForeignKey(ValorCaracteristica, related_name="bandas_con_tipo")
    material = models.ForeignKey(ValorCaracteristica, related_name="bandas_con_material")
    color = models.ForeignKey(ValorCaracteristica, related_name="bandas_con_color")
    ancho = models.PositiveIntegerField(default=0, verbose_name="Ancho (mm)")
    longitud = models.DecimalField(decimal_places=2, max_digits=8, default=1, verbose_name="Longitud (m)")
    material_varilla = models.ForeignKey(ValorCaracteristica, related_name="bandas_con_material_varilla")
    total_filas = models.PositiveIntegerField(default=0)
    # endregion

    # region Empujadores
    con_empujador = models.BooleanField(default=False)
    empujador_tipo = models.ForeignKey(ValorCaracteristica, null=True, blank=True, related_name="bandas_con_tipo_empujador", verbose_name="Tipo")
    empujador_altura = models.PositiveIntegerField(default=0, verbose_name="Altura (mm)")
    empujador_ancho = models.PositiveIntegerField(default=0, verbose_name="Ancho (mm)")
    empujador_distanciado = models.PositiveIntegerField(default=0, null=True, blank=True, verbose_name="Distanciado (mm)")
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

    # region Atributos de activación
    activo = models.BooleanField(default=False, verbose_name="Activo")
    activo_componentes = models.BooleanField(default=False, verbose_name="En Compo.")
    activo_proyectos = models.BooleanField(default=False, verbose_name="En Proy.")
    activo_catalogo = models.BooleanField(default=False, verbose_name="En Cata.")
    # endregion

    # region Precios y Costos
    precio_total = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    costo_base_total = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    rentabilidad = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    # endregion

    objects = models.Manager()
    activos = BandaActivosManager()

    ensamblaje = models.ManyToManyField(
        Producto,
        through='Ensamblado',
        through_fields=('banda', 'producto'),
    )

    def get_absolute_url(self):
        return reverse("bandas:detalle_banda", kwargs={"pk": self.pk})

    def save(self):
        self.actualizar_precio_total()
        super().save()

    def actualizar_precio_total(self):
        """
        Actualiza el precio total, el costo total y calcular la rentabilidad
        desde el precio de cada uno de los módulos.
        """
        precio = 0
        costo_base = 0
        for modulo in self.ensamblado.all():
            precio += modulo.precio_linea
            costo_base += modulo.costo_cop_linea
        self.precio_total = precio
        self.costo_base_total = costo_base
        self.rentabilidad = precio - costo_base


# endregion

# region Ensamblado
class Ensamblado(TimeStampedModel):
    banda = models.ForeignKey(Banda, on_delete=models.CASCADE, related_name='ensamblado')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='ensamblados')

    precio_linea = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    costo_cop_linea = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    rentabilidad = models.DecimalField(max_digits=18, decimal_places=4, default=0)

    ancho = models.PositiveIntegerField(default=0, verbose_name="Ancho (mm)")
    cortado_a = models.CharField(max_length=10, null=True, blank=True)
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad")
    created_by = models.ForeignKey(User, editable=False, null=True, blank=True, related_name="ensamblado_created_by")
    updated_by = models.ForeignKey(User, editable=False, null=True, blank=True, related_name="ensamblado_updated_by")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.precio_linea_original = self.precio_linea

    def save(self):
        self.actualizar_precio_total_linea()
        super().save()
        if self.precio_linea != self.precio_linea_original:
            print("Entro a actualizar banda")
            self.banda.save()

    def actualizar_precio_total_linea(self):
        self.precio_linea = Decimal(self.producto.precio_base) * Decimal(self.cantidad)
        self.costo_cop_linea = Decimal(self.producto.costo_cop) * Decimal(self.cantidad)
        self.rentabilidad = self.precio_linea - self.costo_cop_linea

# endregion

# region CostoEnsamblado
class CostoEnsambladoBlanda(models.Model):
    nombre = models.CharField(max_length=30)
    aleta = models.BooleanField(default=False)
    empujador = models.BooleanField(default=False)
    porcentaje = models.DecimalField(max_digits=5 ,decimal_places=2)

    class Meta:
        unique_together=('aleta','empujador')
# endregion

# endregion
