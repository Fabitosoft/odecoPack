from datetime import datetime

from django.db import models
from django.urls import reverse
from model_utils.models import TimeStampedModel

from usuarios.models import UserExtended, Colaborador

from geografia_colombia.models import Pais, Ciudad, Departamento

from empresas.models import Canal, Industria


# Create your models here.

class GrupoCliente(models.Model):
    nombre = models.CharField(max_length=120, unique=True)

    class Meta:
        verbose_name = 'Grupo Cliente'
        verbose_name_plural = 'I-0.2 Grupos Cliente'

    def __str__(self):
        return self.nombre


class PaisBiable(models.Model):
    pais_id = models.PositiveIntegerField(primary_key=True)
    nombre = models.CharField(max_length=120)

    class Meta:
        verbose_name = 'País'
        verbose_name_plural = 'C-0.1 Paises'

    def __str__(self):
        return self.nombre


class DepartamentoBiable(models.Model):
    departamento_id = models.PositiveIntegerField(primary_key=True)
    nombre = models.CharField(max_length=120)
    pais = models.ForeignKey(PaisBiable)

    class Meta:
        verbose_name = 'Departamento'
        verbose_name_plural = 'C-0.2 Departamentos'

    def __str__(self):
        return self.nombre


class CiudadBiable(models.Model):
    ciudad_id = models.PositiveIntegerField(primary_key=True)
    nombre = models.CharField(max_length=120)
    departamento = models.ForeignKey(DepartamentoBiable)
    ciudad_intranet = models.ForeignKey(Ciudad, null=True, blank=True)

    class Meta:
        verbose_name = 'Ciudad'
        verbose_name_plural = 'C-0.3 Ciudades'

    def __str__(self):
        return self.nombre


class ItemsBiable(models.Model):
    id_item = models.PositiveIntegerField(primary_key=True)
    id_referencia = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=40)
    descripcion_dos = models.CharField(max_length=40)
    activo = models.BooleanField(default=True)
    nombre_tercero = models.CharField(max_length=120)

    linea = models.CharField(max_length=120, null=True, blank=True)
    categoria_mercadeo = models.CharField(max_length=120, null=True, blank=True)
    categoria_mercadeo_dos = models.CharField(max_length=120, null=True, blank=True)
    categoria_mercadeo_tres = models.CharField(max_length=120, null=True, blank=True)
    serie = models.CharField(max_length=30, null=True, blank=True)
    ancho = models.CharField(max_length=60, null=True, blank=True)
    alto = models.CharField(max_length=60, null=True, blank=True)
    longitud = models.CharField(max_length=60, null=True, blank=True)
    diametro = models.CharField(max_length=60, null=True, blank=True)
    dientes = models.CharField(max_length=10, null=True, blank=True)
    material = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=30, null=True, blank=True)

    desc_item_padre = models.CharField(max_length=40)
    unidad_medida_inventario = models.CharField(max_length=6)
    id_procedencia = models.CharField(max_length=1)

    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'C-2.1 Items'

    def __str__(self):
        return self.descripcion


class Cliente(models.Model):
    nit = models.CharField(max_length=20, primary_key=True)
    nombre = models.CharField(max_length=120)
    forma_pago = models.CharField(max_length=120, null=True, blank=True, verbose_name="Forma Pago CGUno")
    grupo = models.ForeignKey(GrupoCliente, null=True, blank=True, related_name='mis_empresas')
    fecha_creacion = models.DateField(null=True, blank=True)
    canal = models.ForeignKey(Canal, related_name='mis_empresas', null=True, blank=True)
    clasificacion = models.CharField(max_length=1, null=True, blank=True)
    industria = models.ForeignKey(Industria, related_name='mis_empresas', null=True, blank=True)
    competencia = models.BooleanField(default=False)
    cerro = models.BooleanField(default=False, verbose_name="Cerró")
    potencial_compra = models.DecimalField(max_digits=10, decimal_places=0, default=0,
                                           verbose_name='Potencial de Compra')
    potencial_compra_fecha_actualizacion = models.DateField(verbose_name='Fecha último Cambio Potencial Compra',
                                                            null=True, blank=True)
    cliente_nuevo_nit = models.ForeignKey('self', null=True, blank=True, related_name='cliente_viejo_nit')

    def get_absolute_url(self):
        return reverse("biable:detalle_cliente", kwargs={"pk": self.nit})

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'C-1.1 Clientes'
        permissions = (
            ('ver_clientes', 'Ver Clientes'),
        )

    def __str__(self):
        return self.nombre


class ActualizacionManager(models.Manager):
    def movimiento_ventas(self):
        return self.filter(tipo='MOVIMIENTO_VENTAS')

    def cartera_vencimiento(self):
        return self.filter(tipo='CARTERA_VENCIMIENTO')


class Actualizacion(models.Model):
    tipo = models.CharField(max_length=100)
    dia = models.PositiveIntegerField()
    mes = models.PositiveIntegerField()
    ano = models.PositiveIntegerField()
    fecha = models.DateTimeField()

    objects = models.Manager()
    tipos = ActualizacionManager()

    def __str__(self):
        return '%s - %s' % (self.tipo, self.fecha)

    def fecha_formateada(self):
        fecha = '%s' % (self.fecha)
        fecha_splited = fecha.split(sep=".", maxsplit=1)
        fecha_splited = fecha_splited[0].split(" ")
        formateada = 'Actualizado el %s a las %s' % (fecha_splited[0], fecha_splited[1])
        return formateada

    def get_ultima_cartera_vencimiento(self):
        return self.tipos.cartera_vencimiento().latest('fecha')


class LineaVendedorBiable(models.Model):
    nombre = models.CharField(max_length=120)

    class Meta:
        verbose_name = 'Linea Vendedor CGUno'
        verbose_name_plural = 'I-0.1 Lineas Vendedor CGUno'

    def __str__(self):
        return self.nombre


class VendedorBiable(models.Model):
    id = models.PositiveIntegerField(primary_key=True, editable=False)
    nombre = models.CharField(max_length=200)
    linea_ventas = models.ForeignKey(LineaVendedorBiable, null=True, blank=True, related_name='mis_vendedores')
    activo = models.BooleanField(default=True)
    colaborador = models.ForeignKey(Colaborador, null=True, blank=True, on_delete=models.PROTECT,
                                    related_name='mi_vendedor_biable')

    class Meta:
        verbose_name = 'Vendedor'
        verbose_name_plural = 'C-1.3 Vendedores'

    def __str__(self):
        return self.nombre


class MovimientoVentaBiable(models.Model):  # Detalle factura
    tipo_documento = models.CharField(max_length=3, null=True, blank=True)
    nro_documento = models.CharField(max_length=10, null=True, blank=True)
    factura = models.ForeignKey('FacturasBiable', null=True, blank=True, related_name='mis_movimientos_venta')
    item_biable = models.ForeignKey(ItemsBiable, null=True, blank=True, related_name='mis_ventas')
    precio_uni = models.DecimalField(max_digits=18, decimal_places=4)
    cantidad = models.DecimalField(max_digits=18, decimal_places=4)
    venta_bruta = models.DecimalField(max_digits=18, decimal_places=4)
    dscto_netos = models.DecimalField(max_digits=18, decimal_places=4)
    costo_total = models.DecimalField(max_digits=18, decimal_places=4)
    rentabilidad = models.DecimalField(max_digits=18, decimal_places=4)
    imp_netos = models.DecimalField(max_digits=18, decimal_places=4)
    venta_neto = models.DecimalField(max_digits=18, decimal_places=4)
    proyecto = models.CharField(max_length=60, null=True, blank=True)

    class Meta:
        permissions = (
            ('reportes_ventas', 'Reportes Ventas'),
            ('reporte_ventas_1', 'R Vent Vend'),
            ('reporte_ventas_2', 'R Conso Ventas'),
            ('reporte_ventas_3', 'R Vent Cli'),
            ('reporte_ventas_4', 'R Vent Cli Año'),
            ('reporte_ventas_5', 'R Vent Cli Mes'),
            ('reporte_ventas_6', 'R Vent Lin Año'),
            ('reporte_ventas_7', 'R Vent Lin Año Mes'),
            ('reporte_ventas_8', 'R Vent Mes'),
            ('reporte_ventas_9', 'R Vent Vend Mes'),
            ('reporte_ventas_10', 'R Vent Pro Año Mes'),
            ('reporte_ventas_todos_vendedores', 'R Vent Vend Todos'),
        )
        verbose_name = 'Movimiento Venta'
        verbose_name_plural = 'T-0.2 Movimiento Ventas'


class Cartera(models.Model):
    vendedor = models.ForeignKey(VendedorBiable, null=True, related_name='mis_carteras')
    id_terc_fa = models.CharField(max_length=20)
    cliente = models.CharField(max_length=200)
    client = models.ForeignKey(Cliente, on_delete=models.PROTECT, null=True)
    tipo_documento = models.CharField(max_length=3, null=True, blank=True)
    nro_documento = models.CharField(max_length=10, null=True, blank=True)
    factura = models.ForeignKey('FacturasBiable', null=True, blank=True, related_name='mis_cartera_venta')
    forma_pago = models.PositiveIntegerField(null=True, blank=True)
    fecha_documento = models.DateField(null=True, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    fecha_ultimo_pago = models.DateField(null=True, blank=True)
    por_cobrar = models.DecimalField(max_digits=18, decimal_places=4)
    retenciones = models.DecimalField(max_digits=18, decimal_places=4)
    valor_contado = models.DecimalField(max_digits=18, decimal_places=4)
    anticipo = models.DecimalField(max_digits=18, decimal_places=4)
    a_recaudar = models.DecimalField(max_digits=18, decimal_places=4)
    recaudado = models.DecimalField(max_digits=18, decimal_places=4)
    debe = models.DecimalField(max_digits=18, decimal_places=4)
    esta_vencido = models.BooleanField(default=False)
    dias_vencido = models.PositiveIntegerField(null=True, blank=True)
    dias_para_vencido = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        permissions = (
            ('ver_carteras', 'R Cart. Vcto'),
            ('ver_carteras_todos', 'R Cart. Vcto Todos'),
        )
        verbose_name = 'Cartera'
        verbose_name_plural = 'T-0.2 Carteras'


class FacturaBiableActivaManager(models.Manager):
    def get_queryset(self):
        return super(FacturaBiableActivaManager, self).get_queryset().filter(activa=True)


class FacturasBiable(TimeStampedModel):
    ciudad_biable = models.ForeignKey(CiudadBiable, null=True, blank=True, on_delete=models.PROTECT)
    fecha_documento = models.DateField(null=True, blank=True)
    direccion_despacho = models.CharField(max_length=400, null=True, blank=True)
    tipo_documento = models.CharField(max_length=3, null=True, blank=True)
    nro_documento = models.CharField(max_length=10, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, null=True, related_name='mis_compras')
    vendedor = models.ForeignKey(VendedorBiable, null=True)
    venta_bruta = models.DecimalField(max_digits=18, decimal_places=4)
    dscto_netos = models.DecimalField(max_digits=18, decimal_places=4)
    costo_total = models.DecimalField(max_digits=18, decimal_places=4)
    rentabilidad = models.DecimalField(max_digits=18, decimal_places=4)
    imp_netos = models.DecimalField(max_digits=18, decimal_places=4)
    venta_neto = models.DecimalField(max_digits=18, decimal_places=4)
    sucursal = models.ForeignKey('SucursalBiable', null=True, blank=True, related_name='mis_facturas')
    activa = models.BooleanField(default=True)

    objects = models.Manager()
    activas = FacturaBiableActivaManager()

    def __str__(self):
        return "%s-%s" % (self.tipo_documento, self.nro_documento)

    def get_absolute_url(self):
        return reverse("biable:detalle_factura", kwargs={"pk": self.pk})

    class Meta:
        permissions = (
            ('ver_info_admon_ventas', 'Ver Info Admon Factura'),
        )
        verbose_name = 'Factura'
        verbose_name_plural = 'T-0.1 Facturas'
        unique_together = ('tipo_documento', 'nro_documento')


class SucursalBiable(models.Model):
    nro_sucursal = models.PositiveIntegerField()
    cliente = models.ForeignKey(Cliente, related_name='mis_sucursales')
    nombre_establecimiento = models.CharField(max_length=200, null=True, blank=True)
    nombre_establecimiento_intranet = models.CharField(max_length=200, null=True, blank=True)
    cupo_credito = models.DecimalField(max_digits=10, decimal_places=0)
    condicion_pago = models.PositiveIntegerField(null=True, blank=True)
    activo = models.BooleanField()
    fecha_creacion = models.DateField()
    direccion = models.CharField(max_length=200)
    vendedor_biable = models.ForeignKey(VendedorBiable, null=True, blank=True, related_name='mis_clientes_biable')
    vendedor_real = models.ForeignKey(VendedorBiable, null=True, blank=True, related_name='mis_clientes_reales')

    def __str__(self):
        if self.nombre_establecimiento_intranet:
            nombre = self.nombre_establecimiento_intranet
        else:
            nombre = self.direccion
        return '%s - %s' % (self.cliente, nombre)

    class Meta:
        unique_together = ('nro_sucursal', 'cliente')
        verbose_name = 'Sucursal Cliente'
        verbose_name_plural = 'C-1.2 Sucursales Cliente'
