from django.db import models


class BandaActivasQuerySet(models.QuerySet):
    def get_queryset(self):
        return BandaActivasQuerySet(self.model, using=self._db).filter(activo=True)

    def catalogo(self):
        return self.get_queryset().filter(activo_catalogo=True)

    def componentes(self):
        return self.get_queryset().filter(activo_componentes=True)

    def proyectos(self):
        return self.get_queryset().filter(activo_proyectos=True)
