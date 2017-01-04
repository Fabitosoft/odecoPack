from django.contrib import admin

from biable.models import VendedorBiable, VendedorBiableUser, LineaVendedorBiable
# Register your models here.

class VendedorBiableAdmin(admin.ModelAdmin):
    list_display = ('nombre','id','linea_ventas','activo')
    list_editable = ('linea_ventas',)
    readonly_fields = ('activo',)

    def get_linea_ventas(self,obj):
        return obj.linea_ventas.nombre
    get_linea_ventas.short_description = 'Línea'



admin.site.register(VendedorBiable,VendedorBiableAdmin)
admin.site.register(VendedorBiableUser)
admin.site.register(LineaVendedorBiable)
