from django.db import models
from django.db.models import Q


class ArticuloCatalogoActivosQuerySet(models.QuerySet):
    def get_queryset(self, **kwarg):
        qs = ArticuloCatalogoActivosQuerySet(self.model, using=self._db).filter(
            Q(cg_uno__activo=True),
            Q(activo=True)
        )
        return qs

    def cg_uno(self):
        qs = self.get_queryset().filter(
            ~Q(cg_uno__ultimo_costo=0) &
            ~Q(origen='LP_INTRANET')
        )
        return qs

    def lista_precios(self):
        qs = self.get_queryset().filter(
            Q(origen='LP_INTRANET')
        )
        return qs
