from django.contrib import admin
from odeco.admin import ViewAdmin
from proveedores.models import Proveedor, MargenProvedor


# Register your models here.

class MargenProvedorInline(admin.TabularInline):
    model = MargenProvedor
    # can_delete = False
    extra = 0


class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'moneda','factor_importacion','factor_importacion_aereo')
    list_editable = ('factor_importacion','factor_importacion_aereo')

    inlines = [
        MargenProvedorInline,
    ]


class MargenProveedorAdmin(admin.ModelAdmin):
    list_filter = ("categoria", "proveedor")
    list_display = ('proveedor', 'categoria', 'margen_deseado')
    list_editable = ('margen_deseado',)

    def save_model(self, request, obj, form, change):
        if form.has_changed():
            obj.save()



admin.site.register(Proveedor, ProveedorAdmin)
admin.site.register(MargenProvedor, MargenProveedorAdmin)
