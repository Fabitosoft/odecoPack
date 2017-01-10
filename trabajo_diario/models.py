from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.signals import post_save

from model_utils.models import TimeStampedModel


# Create your models here.

class TrabajoDia(TimeStampedModel):
    usuario = models.ForeignKey(User)
    nro_tareas = models.PositiveIntegerField(default=0)
    nro_tareas_sin_atender = models.PositiveIntegerField(default=0)
    nro_tareas_atendidas = models.PositiveIntegerField(default=0)
    porcentaje_atendido = models.DecimalField(max_digits=4, decimal_places=1, default=0)

    def __str__(self):
        return "%s - %s" % (self.usuario, self.created.date())

    def get_nro_tareas(self):
        nro_tareas = int(self.mis_tareas.aggregate(Count('id'))['id__count'])
        return nro_tareas

    def get_nro_tareas_sin_atender(self):
        nro_tareas_sin_atender = int(self.mis_tareas.filter(estado=0).aggregate(Count('id'))['id__count'])
        return nro_tareas_sin_atender

    def get_nro_tareas_atendidas(self):
        nro_tareas_atendidas = self.get_nro_tareas() - self.get_nro_tareas_sin_atender()
        return nro_tareas_atendidas

    def get_porcentaje_gestion_tareas(self):
        nro_tareas = self.nro_tareas
        nro_tareas_sin_atender = self.nro_tareas_sin_atender
        nro_tareas_atendidas = nro_tareas - nro_tareas_sin_atender
        porcentaje_tareas_atendidas = 0
        if nro_tareas > 0:
            porcentaje_tareas_atendidas = nro_tareas_atendidas / nro_tareas
        return porcentaje_tareas_atendidas * 100


class TareaDiaria(TimeStampedModel):
    ESTADOS = (
        (0, 'Pendiente'),
        (1, 'Atendida en Proceso'),
        (2, 'Atendida Terminada'),
    )
    mi_dia = models.ForeignKey(TrabajoDia, on_delete=models.CASCADE, related_name='mis_tareas')
    tipo = models.CharField(max_length=120)
    descripcion = models.TextField(max_length=300, null=True, blank=True)
    observacion = models.TextField(max_length=300, null=True, blank=True)
    estado = models.PositiveIntegerField(choices=ESTADOS, default=0)

def set_actualizar_mi_trabajo_diario(sender, instance, created, **kwargs):
    if not created:
        trabajo_dia = instance.mi_dia
        trabajo_dia.nro_tareas_sin_atender = trabajo_dia.get_nro_tareas_sin_atender()
        trabajo_dia.nro_tareas = trabajo_dia.get_nro_tareas()
        trabajo_dia.nro_tareas_atendidas = trabajo_dia.get_nro_tareas_atendidas()
        trabajo_dia.save()
        trabajo_dia.porcentaje_atendido = trabajo_dia.get_porcentaje_gestion_tareas()
        trabajo_dia.save()

post_save.connect(set_actualizar_mi_trabajo_diario, sender=TareaDiaria)