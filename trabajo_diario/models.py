from django.db import models
from django.contrib.auth.models import User

from model_utils.models import TimeStampedModel


# Create your models here.

class TrabajoDia(TimeStampedModel):
    usuario = models.ForeignKey(User)

    def __str__(self):
        return "%s - %s"%(self.usuario,self.created.date())


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
