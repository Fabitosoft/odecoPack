from django.contrib import admin

from import_export.admin import ImportExportModelAdmin

from productos.models import UnidadMedida,Producto
from listasprecios.models import ListaPrecio
# Register your models here.

class ListaPrecioInline(admin.TabularInline):
    model = ListaPrecio
    extra = 0


class ProductoAdmin(ImportExportModelAdmin):
    list_display = ('referencia','descripcion_estandar','unidad_medida','activo','activo_ensamble','activo_proyectos','activo_componentes','activo_catalogo')
    search_fields = ['referencia','descripcion_estandar']
    list_editable = ['activo','activo_ensamble','activo_proyectos','activo_componentes','activo_catalogo']
    inlines = [
        ListaPrecioInline,
    ]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        else:
            obj.updated_by = request.user
        obj.save()

admin.site.register(UnidadMedida)
admin.site.register(Producto,ProductoAdmin)