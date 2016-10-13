from django.contrib import admin

from importaciones.models import Moneda, FactorCambioMoneda


class FactorCambioMonedaAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Informacion General', {
            'classes': ('form-control',),
            'fields':
                (
                    'moneda_origen',
                    'cambio'
                )
        })
        ,)

    list_display = ("moneda_origen", "cambio")
    list_editable = ("cambio",)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('moneda_origen',)
        return self.readonly_fields


# Register your models here.

admin.site.register(Moneda)
admin.site.register(FactorCambioMoneda, FactorCambioMonedaAdmin)
