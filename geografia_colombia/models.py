from django.db import models


# Create your models here.

class Pais(models.Model):
    nombre = models.CharField(max_length=120, unique=True)

    class Meta:
        verbose_name = 'País'
        verbose_name_plural = 'Paises'

    def __str__(self):
        return self.nombre


class Departamento(models.Model):
    nombre = models.CharField(max_length=120)
    pais = models.ForeignKey(Pais, related_name='mis_departamentos')

    class Meta:
        unique_together = ('nombre', 'pais')

    def __str__(self):
        return self.nombre



class Ciudad(models.Model):
    nombre = models.CharField(max_length=120)
    departamento = models.ForeignKey(Departamento, related_name="mis_municipios", on_delete=models.PROTECT)

    class Meta:
        unique_together = ('nombre', 'departamento')

    def __str__(self):
        return '%s - %s - %s' % (self.nombre, self.departamento.nombre,self.departamento.pais.nombre)
