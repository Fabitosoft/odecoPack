from django.db import models
from django.db.models import Q


class ProductoQuerySet(models.QuerySet):
    def modulos(self):
        return self.filter(activo_ensamble=True)

    def catalogo(self):
        return self.filter(activo_catalogo=True)

    def componentes(self):
        return self.filter(activo_componentes=True)

    def proyectos(self):
        return self.filter(activo_proyectos=True)


class ArticuloCatalogoActivosQuerySet(models.QuerySet):
    def get_queryset(self, **kwarg):
        qs = ArticuloCatalogoActivosQuerySet(self.model, using=self._db).filter(
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

    def todos(self):
        return self.get_queryset()
