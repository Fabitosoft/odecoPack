from django.contrib import admin

from import_export.admin import ImportExportModelAdmin

from productos.models import UnidadMedida,Producto
from listasprecios.models import ListaPrecio
# Register your models here.

class ListaPrecioInline(admin.TabularInline):
    model = ListaPrecio
    extra = 0

class ProductoAdmin(ImportExportModelAdmin):
    list_display = ('referencia','descripcion_estandar','unidad_medida')
    search_fields = ['referencia','descripcion_estandar']
    inlines = [
        ListaPrecioInline,
    ]

admin.site.register(UnidadMedida)
admin.site.register(Producto,ProductoAdmin)