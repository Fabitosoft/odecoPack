from django.contrib.auth.models import User
from django.db import models
from django.core.validators import RegexValidator
from django.db.models.signals import post_save, post_delete

from utils.models import TimeStampedModel
from productos.models import Producto
# Create your models here.
class Cotizacion(TimeStampedModel):
    ESTADOS = (
        ('INI', 'Iniciado'),
        ('ENV', 'Enviada'),
    )
    estado = models.CharField(max_length=10, choices=ESTADOS, default='INI')
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    nro_contacto = models.CharField(validators=[phone_regex], blank=True, max_length=15)  # validators should be a list
    email = models.EmailField(max_length=150, blank=True)
    nombres_contacto = models.CharField(max_length=120, blank=True)
    apellidos_contacto = models.CharField(max_length=120, blank=True)
    razon_social = models.CharField(max_length=120, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    usuario = models.ForeignKey(User, default=1)

    def update_total(self):
        "updating..."
        total = 0
        items = self.items.all()
        for item in items:
            print(item.total)
            total += item.total
        self.total = "%.2f" % (total)
        self.save()

class ItemCotizacion(TimeStampedModel):
    cotizacion = models.ForeignKey(Cotizacion, related_name="items")
    item = models.ForeignKey(Producto, related_name="cotizaciones")
    cantidad = models.DecimalField(max_digits=10, decimal_places=0)
    precio = models.DecimalField(max_digits=10, decimal_places=0)
    total = models.DecimalField(max_digits=10, decimal_places=0)

def cotizacion_item_post_save_receiver(sender, instance, *args, **kwargs):
	instance.cotizacion.update_total()

post_save.connect(cotizacion_item_post_save_receiver, sender=ItemCotizacion)
post_delete.connect(cotizacion_item_post_save_receiver, sender=ItemCotizacion)

