from django.db import models


# Create your models here.
class Departamento(models.Model):
    nombre = models.CharField(max_length=120)



class Ciudad(models.Model):
    nombre = models.CharField(max_length=120)
    departamento = models.ForeignKey(Departamento, related_name="mis_municipios", on_delete=models.PROTECT)
