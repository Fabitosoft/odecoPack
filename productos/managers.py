from django.db import models
from django.db.models import Q


class ArticuloCatalogoActivosQuerySet(models.QuerySet):
    def get_queryset(self, **kwarg):
        qs = ArticuloCatalogoActivosQuerySet(self.model, using=self._db)
        return qs

    def cg_uno(self):
        qs = self.get_queryset().filter(
            Q(cg_uno__activo=True) &
            ~Q(cg_uno__ultimo_costo=0) &
            ~Q(origen='LP_INTRANET')
        )
        return qs

    def lista_precios(self):
        qs = self.get_queryset().filter(
            Q(activo=True) &
            Q(origen='LP_INTRANET')
        )
        return qs

    def all(self):
        qs1 = self.cg_uno()
        qs2 = self.lista_precios()
        return qs1 | qs2
