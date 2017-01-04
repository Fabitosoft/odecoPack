from django.contrib import admin

from biable.models import VendedorBiable, LineaVendedorBiable,Cliente
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

admin.site.register(Cliente,ClienteBiableAdmin)
admin.site.register(VendedorBiable,VendedorBiableAdmin)
admin.site.register(LineaVendedorBiable)
