from django.contrib.auth.models import User
from django.db import models
from django.core.validators import RegexValidator
from django.db.models.signals import post_save, post_delete
from django.urls import reverse

from bandas.models import Banda
from utils.models import TimeStampedModel
from productos.models import Producto
from listasprecios.models import FormaPago


# Create your models here.
# region Cotizaciones
class CotizacionesEstadosManager(models.Manager):
    def iniciado(self):
        return self.get_queryset().filter(estado='INI')

    def enviado(self, **kwarg):
        usuario = kwarg.get("usuario")
        qs = self.get_queryset().filter(estado='ENV')
        if usuario:
            qs = qs.filter(usuario=usuario)
        return qs


class Cotizacion(TimeStampedModel):
    ESTADOS = (
        ('INI', 'Iniciado'),
        ('ENV', 'Enviada'),
    )
    estado = models.CharField(max_length=10, choices=ESTADOS, default='INI')
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    nro_contacto = models.CharField(validators=[phone_regex], blank=True, max_length=15)  # validators should be a list
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

    estados = CotizacionesEstadosManager()
    objects = models.Manager()

    class Meta:
        permissions = (
            ('full_cotizacion', 'Full Cotizacion'),
        )

    def get_absolute_url(self):
        return reverse("cotizaciones:detalle_cotizacion", kwargs={"pk": self.pk})

    def update_total(self):
        "updating..."
        total = 0
        items = self.items.all()
        for item in items:
            print(item.total)
            total += item.total
        self.total = "%.2f" % total
        self.save()

    def get_rentabilidad_actual_total(self):
        rentabilidad = 0
        for item in self.items.all():
            rentabilidad += item.get_rentabilidad_actual_total()
        return rentabilidad

    def __str__(self):
        return "%s" %self.nro_cotizacion


# endregion

# region ItemCotizacion
class ItemCotizacion(TimeStampedModel):
    cotizacion = models.ForeignKey(Cotizacion, related_name="items")
    item = models.ForeignKey(Producto, related_name="cotizaciones", null=True)
    banda = models.ForeignKey(Banda, related_name="cotizaciones", null=True)
    cantidad = models.DecimalField(max_digits=18, decimal_places=3)
    precio = models.DecimalField(max_digits=18, decimal_places=0)
    forma_pago = models.ForeignKey(FormaPago, related_name="items_cotizaciones")
    total = models.DecimalField(max_digits=18, decimal_places=0)
    dias_entrega = models.PositiveIntegerField(default=0)

    def get_nombre_item(self):
        if self.item:
            nombre = self.item.descripcion_estandar
        else:
            nombre = self.banda.descripcion_estandar
        return nombre

    def get_referencia_item(self):
        if self.item:
            nombre = self.item.referencia
        else:
            nombre = self.banda.referencia
        return nombre

    def get_unidad_item(self):
        if self.item:
            nombre = self.item.unidad_medida
        else:
            nombre = "Metro"
        return nombre

    def get_costo_cop_actual_unidad(self):
        if self.item:
            costo = self.item.costo_cop
        else:
            costo = self.banda.costo_base_total
        return round(costo, 0)

    def get_costo_cop_actual_total(self):
        if self.item:
            costo = self.item.costo_cop
        else:
            costo = self.banda.costo_base_total
        return round(costo * self.cantidad, 0)

    def get_rentabilidad_actual_total(self):
        costo = self.get_costo_cop_actual_total()
        return round(self.total - costo, 0)

    def get_margen_rentabilidad_actual(self):
        return round((self.get_rentabilidad_actual_total() * 100) / self.total, 2)

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
    nro_remision = models.PositiveIntegerField()
    nro_factura = models.PositiveIntegerField()
    fecha_prometida_entrega = models.DateField()
    entregado = models.BooleanField(default=False)
    cotizacion = models.ForeignKey(Cotizacion, related_name="mis_remisiones")

    class Meta:
        verbose_name_plural = "Remisiones x Cotización"

    def __str__(self):
        return "%s" % self.nro_remision
# endregion
