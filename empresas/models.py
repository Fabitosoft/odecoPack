from django.db import models

from utils.models import TimeStampedModel


# Create your models here.

class Canal(TimeStampedModel):
    canal = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "canales"

    def __str__(self):
        return self.canal
