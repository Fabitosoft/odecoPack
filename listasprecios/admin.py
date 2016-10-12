from django.contrib import admin

# Register your models here.
from import_export.admin import ImportExportModelAdmin

from listasprecios.models import FormaPago, CategoriaMargen


class FormaPagoAdmin(admin.ModelAdmin):
    list_display = ('canal', 'forma', 'porcentaje')
    list_editable = ('porcentaje',)


admin.site.register(FormaPago, FormaPagoAdmin)
admin.site.register(CategoriaMargen)
