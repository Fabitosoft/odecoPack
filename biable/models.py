from datetime import datetime

from django.db import models


from usuarios.models import UserExtended


# Create your models here.

class Actualizacion(models.Model):
    tipo = models.CharField(max_length=100)
    dia = models.PositiveIntegerField()
    mes = models.PositiveIntegerField()
    ano = models.PositiveIntegerField()
    fecha = models.DateTimeField()

    def __str__(self):
        return '%s - %s' %(self.tipo,self.fecha)

    def fecha_formateada(self):
        fecha = '%s'%(self.fecha)
        fecha_splited = fecha.split(sep=".",maxsplit=1)
        fecha_splited = fecha_splited[0].split(" ")
        formateada = 'Actualizado el %s a las %s'%(fecha_splited[0],fecha_splited[1])
        return formateada


class VendedorBiable(models.Model):
    LINEAS = (
        (1, 'Proyectos'),
        (2, 'Bandas y Componentes'),
        (3, 'Posventa'),
        (4, 'Sin Definir'),
    )
    id = models.PositiveIntegerField(primary_key=True, editable=False)
    nombre = models.CharField(max_length=200)
    linea = models.PositiveIntegerField(choices=LINEAS, default=4)
    activo = models.BooleanField(default=True, editable=False)

    def __str__(self):
        return self.nombre

class VendedorBiableUser(models.Model):
    usuario = models.ForeignKey(UserExtended, related_name='mis_vendedores')
    vendedores = models.ManyToManyField(VendedorBiable, related_name='mis_auditores')

    def __str__(self):
        return self.usuario.user.get_full_name()

    class Meta:
        verbose_name_plural = "Vendedores por usuario para Indicadores"

class MovimientoVentaBiable(models.Model):
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    day = models.PositiveIntegerField()
    vendedor = models.ForeignKey(VendedorBiable,null=True)
    id_terc_fa = models.CharField(max_length=20)
    cliente = models.CharField(max_length=200)
    proyecto = models.CharField(max_length=10)
    tipo_documento = models.CharField(max_length=3, null=True, blank=True)
    nro_documento = models.CharField(max_length=10, null=True, blank=True)
    item_id = models.PositiveIntegerField()
    precio_uni = models.DecimalField(max_digits=18, decimal_places=4)
    cantidad = models.DecimalField(max_digits=18, decimal_places=4)
    venta_bruta = models.DecimalField(max_digits=18, decimal_places=4)
    dscto_netos = models.DecimalField(max_digits=18, decimal_places=4)
    costo_total = models.DecimalField(max_digits=18, decimal_places=4)
    rentabilidad = models.DecimalField(max_digits=18, decimal_places=4)
    imp_netos = models.DecimalField(max_digits=18, decimal_places=4)
    venta_neto = models.DecimalField(max_digits=18, decimal_places=4)

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
        )

class Cartera(models.Model):
    vendedor = models.ForeignKey(VendedorBiable,null=True)
    id_terc_fa = models.CharField(max_length=20)
    cliente = models.CharField(max_length=200)
    tipo_documento = models.CharField(max_length=3, null=True, blank=True)
    nro_documento = models.CharField(max_length=10, null=True, blank=True)
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