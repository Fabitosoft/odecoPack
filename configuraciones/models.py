from django.db import models

from solo.models import SingletonModel


# Create your models here.
class EmailConfiguration(SingletonModel):
    email_ventas_from = models.EmailField(null=True, blank=True)

    def __str__(self):
        return "Correos Electrónicos"

    class Meta:
        verbose_name = "Correos Electrónicos"


class DominiosEmail(models.Model):
    dominio = models.CharField(max_length=120, null=False, blank=False)

    class Meta:
        verbose_name = "Dominios Correos Electrónicos"

    def __str__(self):
        return self.dominio
