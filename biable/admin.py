from django.contrib import admin

from biable.models import VendedorBiable, LineaVendedorBiable,Cliente, FacturasBiable
# Register your models here.

class VendedorBiableAdmin(admin.ModelAdmin):
    list_display = ('nombre','id','linea_ventas','activo','colaborador')
    list_editable = ('linea_ventas','colaborador')
    readonly_fields = ('activo',)

    def get_linea_ventas(self,obj):
        return obj.linea_ventas.nombre
    get_linea_ventas.short_description = 'Línea'


class ClienteBiableAdmin(admin.ModelAdmin):
    list_display = ('nit','nombre')

    search_fields = [
        'nit',
        'nombre',
    ]

    readonly_fields = ('nit','nombre',)

class FacturasBiableAdmin(admin.ModelAdmin):
    list_select_related = ['cliente','vendedor']
    list_filter = ('tipo_documento','year','month','day','vendedor')
    search_fields = ('nro_documento','tipo_documento','cliente__nombre')
    list_display = ('nro_documento','tipo_documento','cliente','vendedor')
    readonly_fields = (
        'year',
        'month',
        'day',
        'tipo_documento',
        'nro_documento',
        'cliente',
        'venta_bruta',
        'dscto_netos',
        'costo_total',
        'rentabilidad',
        'imp_netos',
        'venta_neto'
    )


admin.site.register(Cliente,ClienteBiableAdmin)
admin.site.register(VendedorBiable,VendedorBiableAdmin)
admin.site.register(LineaVendedorBiable)
admin.site.register(FacturasBiable,FacturasBiableAdmin)
