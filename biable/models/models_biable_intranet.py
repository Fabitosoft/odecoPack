from django.db import models

from model_utils.models import TimeStampedModel

from .managers import ActualizacionManager


class GrupoCliente(models.Model):
    nombre = models.CharField(max_length=120, unique=True)

    class Meta:
        verbose_name = 'Grupo Cliente'
        verbose_name_plural = 'I-0.2 Grupos Cliente'

    def __str__(self):
        return self.nombre


class LineaVendedorBiable(models.Model):
    nombre = models.CharField(max_length=120)

    class Meta:
        verbose_name = 'Linea Vendedor CGUno'
        verbose_name_plural = 'I-0.1 Lineas Vendedor CGUno'

    def __str__(self):
        return self.nombre


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


class SeguimientoCliente(TimeStampedModel):
    TIPO_CHOICES = (
        ("LLAMADA", 'Llamada'),
        ("VISITA", 'Visita'),
        ("CORREO", 'Correo'),
    )

    cliente = models.ForeignKey('biable.Cliente', related_name='seguimientos')
    tipo = models.CharField(choices=TIPO_CHOICES, max_length=20)
    contacto = models.ForeignKey('contactos.ContactoEmpresa', null=True, blank=True)
    asunto = models.CharField(max_length=150)
    descripcion = models.TextField()
    fecha_seguimiento = models.DateField()
    hora_inicial = models.TimeField()
    hora_final = models.TimeField(null=True, blank=True)
