from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources

from biable.models import (
    VendedorBiable,
    LineaVendedorBiable,
    Cliente,
    FacturasBiable,
    ItemsBiable,
    Cartera,
    MovimientoVentaBiable,
    DepartamentoBiable, PaisBiable, CiudadBiable)


# Register your models here.

class ItemResource(resources.ModelResource):
    class Meta:
        model = ItemsBiable
        import_id_fields = ('id_item',)


class ItemsBiableAdmin(ImportExportModelAdmin):
    list_display = (
        'id_item',
        'id_referencia',
        'descripcion',
        'descripcion_dos',
        'activo',
        'nombre_tercero',
        'desc_item_padre',
        'unidad_medida_inventario',
        'id_procedencia',
        'linea',
        'categoria_mercadeo',
        'categoria_mercadeo_dos',
        'categoria_mercadeo_tres',
        'serie',
    )
    resource_class = ItemResource
    list_editable = (
        'serie',
        'linea',
        'categoria_mercadeo',
        'categoria_mercadeo_dos',
        'categoria_mercadeo_tres',
    )
    readonly_fields = (
        'id_item', 'id_referencia', 'descripcion', 'descripcion_dos', 'activo', 'nombre_tercero', 'desc_item_padre',
        'unidad_medida_inventario', 'id_procedencia')

    search_fields = (
        'id_item',
        'id_referencia',
        'descripcion',
        'descripcion_dos',
        'nombre_tercero',
        'serie',
        'linea',
        'categoria_mercadeo',
        'categoria_mercadeo_dos',
        'categoria_mercadeo_tres',
    )

    list_filter = (
        'activo',
        'id_procedencia',
        'serie',
        'linea',
        'categoria_mercadeo',
    )


class VendedorBiableAdmin(admin.ModelAdmin):
    list_select_related = ['linea_ventas', 'colaborador']
    list_display = ('nombre', 'id', 'linea_ventas', 'activo', 'colaborador')
    list_editable = ('linea_ventas', 'colaborador')
    readonly_fields = ('activo',)

    def get_linea_ventas(self, obj):
        return obj.linea_ventas.nombre

    get_linea_ventas.short_description = 'Línea'


class ClienteBiableAdmin(admin.ModelAdmin):
    list_display = ('nit', 'nombre')

    search_fields = [
        'nit',
        'nombre',
    ]

    readonly_fields = ('nit', 'nombre',)


class FacturasBiableAdmin(admin.ModelAdmin):
    list_select_related = ['cliente', 'vendedor']
    list_filter = ('tipo_documento', 'year', 'month', 'day', 'vendedor')
    search_fields = ('nro_documento', 'tipo_documento', 'cliente__nombre')
    list_display = ('nro_documento', 'tipo_documento', 'cliente', 'vendedor')
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


class CarteraAdmin(admin.ModelAdmin):
    list_display = (
        'tipo_documento', 'nro_documento', 'fecha_documento', 'fecha_vencimiento', 'esta_vencido', 'dias_vencido')
    search_fields = ('vendedor__nombre', 'tipo_documento', 'nro_documento')
    list_filter = ('tipo_documento', 'esta_vencido')


class PaisAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
    readonly_fields = ('nombre','pais_id')


class DepartamentoAdmin(admin.ModelAdmin):
    list_select_related = ('pais',)
    list_display = ('nombre', 'pais',)
    list_filter = ('pais',)
    search_fields = ('nombre', 'pais__nombre',)
    readonly_fields = ('nombre', 'pais','departamento_id')


class CiudadAdmin(admin.ModelAdmin):
    list_select_related = ('departamento', 'ciudad_intranet')
    list_display = ('nombre', 'departamento', 'ciudad_intranet')
    list_filter = ('departamento', 'departamento__pais')
    search_fields = ('nombre', 'departamento__nombre', 'ciudad_intranet__nombre')
    list_editable = ('ciudad_intranet',)
    raw_id_fields = ('ciudad_intranet',)
    readonly_fields = ('nombre', 'departamento', 'ciudad_intranet','ciudad_id')



admin.site.register(DepartamentoBiable, DepartamentoAdmin)
admin.site.register(PaisBiable, PaisAdmin)
admin.site.register(CiudadBiable, CiudadAdmin)
admin.site.register(Cliente, ClienteBiableAdmin)
admin.site.register(VendedorBiable, VendedorBiableAdmin)
admin.site.register(LineaVendedorBiable)
admin.site.register(FacturasBiable, FacturasBiableAdmin)
admin.site.register(ItemsBiable, ItemsBiableAdmin)
admin.site.register(Cartera, CarteraAdmin)
admin.site.register(MovimientoVentaBiable)
