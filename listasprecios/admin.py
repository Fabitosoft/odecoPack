from django.contrib import admin

# Register your models here.
from import_export.admin import ImportExportModelAdmin

from listasprecios.models import VariableListaPrecio, FormaPago,CategoriaMargen


class VariableListaPrecioAdmin(admin.ModelAdmin):
    list_display = ('forma_pago', 'value')


admin.site.register(VariableListaPrecio, VariableListaPrecioAdmin)
admin.site.register(FormaPago)
admin.site.register(CategoriaMargen)
