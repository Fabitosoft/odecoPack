from django.db import models

from cotizaciones.models import Cotizacion
from utils.models import TimeStampedModel
# Create your models here.

class Tarea(TimeStampedModel):
    nombre = models.CharField(max_length=120)
    descripcion = models.CharField(max_length=120)
    fecha_inicial = models.DateField()
    fecha_final = models.DateField()
    esta_finalizada = models.BooleanField(default=False)
    cotizacion = models.ForeignKey(Cotizacion, null=True, blank=True, related_name="mis_tareas")

    class Meta:
        verbose_name_plural="Tareas"

    def __str__(self):
        return "%s" %self.nombre