import datetime

from django.contrib.auth.models import User
from django.db import models
from django.core.validators import RegexValidator
from django.db.models import Q
from django.db.models.signals import post_save, post_delete
from django.urls import reverse

from bandas.models import Banda
from utils.models import TimeStampedModel
from productos.models import Producto, ArticuloCatalogo
from listasprecios.models import FormaPago


# Create your models here.
# region Cotizaciones
class CotizacionesEstadosQuerySet(models.QuerySet):
    def activas(self):
        return self.filter(
            ~Q(estado='ELI') &
            ~Q(estado='FIN')
        )

    def rechazadas(self):
        return self.filter(
            estado='ELI'
        )

    def completadas(self):
        return self.filter(
            estado='FIN'
        )

    def enviadas(self):
        return self.filter(estado='ENV')


class CotizacionesEstadosManager(models.Manager):
    def get_queryset(self, **kwarg):
        usuario = kwarg.get("usuario")
        qs = CotizacionesEstadosQuerySet(self.model, using=self._db)
        if usuario:
            qs = qs.filter(usuario=usuario)
        return qs

    def enviado(self, **kwarg):
        return self.get_queryset(**kwarg).enviadas()

    def activo(self, **kwarg):
        return self.get_queryset(**kwarg).activas()

    def rechazado(self, **kwarg):
        return self.get_queryset(**kwarg).rechazadas()

    def completado(self, **kwarg):
        return self.get_queryset(**kwarg).completadas()


class Cotizacion(TimeStampedModel):
    ESTADOS = (
        ('INI', 'Iniciado'),
        ('ENV', 'Enviada'),
        ('ELI', 'Rechazada'),
        ('REC', 'Recibida'),
        ('PRO', 'En Proceso'),
        ('FIN', 'Entragada Totalmente'),
    )
    estado = models.CharField(max_length=10, choices=ESTADOS, default='INI')
    nro_contacto = models.CharField(blank=True, max_length=30)  # validators should be a list
    email = models.EmailField(max_length=150, blank=True)
    nombres_contacto = models.CharField(max_length=120, blank=True)
    pais = models.CharField(max_length=120, blank=True)
    ciudad = models.CharField(max_length=120, blank=True)
    apellidos_contacto = models.CharField(max_length=120, blank=True)
    razon_social = models.CharField(max_length=120, blank=True)
    nro_cotizacion = models.CharField(max_length=120)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    total = models.DecimalField(max_digits=18, decimal_places=0, default=0)
    usuario = models.ForeignKey(User, default=1)
    observaciones = models.TextField(max_length=300, blank=True, null=True)

    estados = CotizacionesEstadosManager()
    objects = models.Manager()

    class Meta:
        permissions = (
            ('full_cotizacion', 'Full Cotizacion'),
            ('gestion_cotizaciones', 'Gestionar Cotizaciones'),
            # ('hacer_cotizacion', 'Hacer Cotización'),
        )

    def get_absolute_url(self):
        return reverse("cotizaciones:detalle_cotizacion", kwargs={"pk": self.pk})

    def update_total(self):
        "updating..."
        total = 0
        items = self.items.all()
        for item in items:
            total += item.total
        self.total = "%.2f" % total
        self.save()

    def set_estado(self, estado):
        self.estado = estado
        self.save()

    def get_rentabilidad_actual_total(self):
        rentabilidad = 0
        for item in self.items.all():
            rentabilidad += item.get_rentabilidad_actual_total()
        return rentabilidad

    def __str__(self):
        return "%s" % self.nro_cotizacion


# endregion

# region ItemCotizacion
class ItemCotizacion(TimeStampedModel):
    cotizacion = models.ForeignKey(Cotizacion, related_name="items")
    item = models.ForeignKey(Producto, related_name="cotizaciones", null=True)
    banda = models.ForeignKey(Banda, related_name="cotizaciones", null=True)
    articulo_catalogo = models.ForeignKey(ArticuloCatalogo, related_name="cotizaciones", null=True)
    cantidad = models.DecimalField(max_digits=18, decimal_places=3, null=True)
    precio = models.DecimalField(max_digits=18, decimal_places=0)
    forma_pago = models.ForeignKey(FormaPago, related_name="items_cotizaciones", null=True)
    p_n_lista_descripcion = models.CharField(max_length=120, null=True, verbose_name='Descripción Otro')
    p_n_lista_referencia = models.CharField(max_length=120, null=True,verbose_name='Referencia Otro', blank=True)
    p_n_lista_unidad_medida = models.CharField(max_length=120, null=True,verbose_name='Unidad Medida')
    total = models.DecimalField(max_digits=18, decimal_places=0)
    dias_entrega = models.PositiveIntegerField(default=0)

    def get_nombre_item(self):
        if self.item:
            nombre = self.item.descripcion_comercial
        elif self.articulo_catalogo:
            nombre = self.articulo_catalogo.nombre
        elif self.banda:
            nombre = self.banda.descripcion_comercial
        else:
            nombre = self.p_n_lista_descripcion
        return nombre

    def get_referencia_item(self):
        if self.item:
            nombre = self.item.referencia
        elif self.articulo_catalogo:
            nombre = self.articulo_catalogo.referencia
        elif self.banda:
            nombre = self.banda.referencia
        else:
            nombre = self.p_n_lista_referencia
        return nombre

    def get_unidad_item(self):
        if self.item:
            nombre = self.item.unidad_medida
        elif self.articulo_catalogo:
            nombre = self.articulo_catalogo.unidad_medida
        elif self.banda:
            nombre = "Metro"
        else:
            nombre = self.p_n_lista_unidad_medida
        return nombre

    def get_costo_cop_actual_unidad(self):
        if self.item:
            costo = self.item.get_costo_cop()
        elif self.articulo_catalogo:
            costo = self.articulo_catalogo.get_costo_cop()
        elif self.banda:
            costo = self.banda.get_costo_cop()
        else:
            costo = 0
        return round(costo, 0)

    def get_costo_cop_actual_total(self):
        return round(self.get_costo_cop_actual_unidad() * self.cantidad, 0)

    def get_rentabilidad_actual_total(self):
        costo = self.get_costo_cop_actual_total()
        return round(self.total - costo, 0)

    def get_margen_rentabilidad_actual(self):
        margen = 0
        if self.total != 0:
            round((self.get_rentabilidad_actual_total() * 100) / self.total, 2)
        return margen

    def get_tiempo_entrega_prometido(self):
        if self.dias_entrega == 0:
            return "Inmediato"
        if self.dias_entrega == 1:
            return "%s dia" % self.dias_entrega
        return "%s dias" % self.dias_entrega


def cotizacion_item_post_save_receiver(sender, instance, *args, **kwargs):
    instance.cotizacion.update_total()


post_save.connect(cotizacion_item_post_save_receiver, sender=ItemCotizacion)
post_delete.connect(cotizacion_item_post_save_receiver, sender=ItemCotizacion)


# endregion

# region Remisiones
class RemisionCotizacion(TimeStampedModel):
    nro_remision = models.CharField(max_length=10)
    nro_factura = models.CharField(max_length=10)
    fecha_prometida_entrega = models.DateField()
    entregado = models.BooleanField(default=False)
    cotizacion = models.ForeignKey(Cotizacion, related_name="mis_remisiones")

    class Meta:
        verbose_name_plural = "Remisiones x Cotización"

    def __str__(self):
        return "%s" % self.nro_remision

    def get_dias_a_fecha_fin(self):
        return (self.fecha_prometida_entrega - datetime.date.today()).days


# endregion

# region Tareas
class TareaCotizacion(TimeStampedModel):
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(max_length=300)
    fecha_inicial = models.DateField()
    fecha_final = models.DateField()
    esta_finalizada = models.BooleanField(default=False)
    cotizacion = models.ForeignKey(Cotizacion, null=True, blank=True, related_name="mis_tareas")

    class Meta:
        verbose_name_plural = "Tareas"

    def __str__(self):
        return "%s" % self.nombre

    def get_dias_a_fecha_fin(self):
        return (self.fecha_final - datetime.date.today()).days

class ComentarioCotizacion(TimeStampedModel):
    comentario = models.TextField(max_length=300)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='comentarios_cotizaciones')
    cotizacion = models.ForeignKey(Cotizacion, null=True, blank=True, related_name="mis_comentarios")


    class Meta:
        ordering = ['-created']

# endregion
