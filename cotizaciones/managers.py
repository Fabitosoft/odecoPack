from django.db import models
from django.db.models import Q


class CotizacionesEstadosQuerySet(models.QuerySet):
    def get_queryset(self, **kwarg):
        usuario = kwarg.get("usuario")
        qs = CotizacionesEstadosQuerySet(self.model, using=self._db)
        return qs

    def activo(self):
        return self.get_queryset().filter(
            ~Q(estado='ELI') &
            ~Q(estado='FIN')
        )

    def rechazado(self):
        return self.get_queryset().filter(
            estado='ELI'
        )

    def completado(self):
        return self.get_queryset().filter(
            estado='FIN'
        )

    def enviado(self):
        return self.get_queryset().filter(estado='ENV')
