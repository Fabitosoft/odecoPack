from django.db import models


class FacturaBiableActivaManager(models.Manager):
    def get_queryset(self):
        return super(FacturaBiableActivaManager, self).get_queryset().filter(activa=True)


class ActualizacionManager(models.Manager):
    def movimiento_ventas(self):
        return self.filter(tipo='MOVIMIENTO_VENTAS')

    def cartera_vencimiento(self):
        return self.filter(tipo='CARTERA_VENCIMIENTO')
