from django.contrib import admin

from importaciones.models import Moneda, FactorCambioMoneda

# Register your models here.

admin.site.register(Moneda)
admin.site.register(FactorCambioMoneda)
