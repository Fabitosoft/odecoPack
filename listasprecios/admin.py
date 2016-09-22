from django.contrib import admin

# Register your models here.
from import_export.admin import ImportExportModelAdmin

from listasprecios.models import ListaPrecio, VariableListaPrecio, FormaPago, VariableBasica


class ListaPrecioAdmin(ImportExportModelAdmin):
    list_display = ('get_referencia','producto', 'proveedor',
                    'get_moneda','cantidad_minima','get_unidadMedida','valor')

    search_fields = ['producto__referencia','producto__descripcion_estandar','producto__descripcion_comercial']

    def get_referencia(self, obj):
        return obj.producto.referencia
    get_referencia.short_description = 'Referencia'

    def get_moneda(self, obj):
        return obj.proveedor.moneda
    get_moneda.short_description = 'Moneda'

    def get_unidadMedida(self, obj):
        return obj.producto.unidad_medida
    get_unidadMedida.short_description = 'UM'

admin.site.register(ListaPrecio,ListaPrecioAdmin)


class VariableListaPrecioAdmin(admin.ModelAdmin):
    list_display = ('forma_pago', 'value')

admin.site.register(VariableListaPrecio,VariableListaPrecioAdmin)
admin.site.register(FormaPago)
admin.site.register(VariableBasica)