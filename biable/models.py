from django.db import models

# Create your models here.
class DataBiable(models.Model):
    vende_nombre = models.CharField(max_length=120, blank=True, null=True)
    vende_id = models.CharField(max_length=4, blank=True, null=True)
    tipo_docu_id = models.CharField(max_length=2, blank=True, null=True)