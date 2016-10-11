from django.contrib import admin

from proveedores.models import Proveedor, MargenProvedor
# Register your models here.

class MargenProvedorInline(admin.TabularInline):
    model = MargenProvedor
    # can_delete = False
    extra = 0

class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'moneda')

    inlines = [
        MargenProvedorInline,
    ]

class MargenProveedorAdmin(admin.ModelAdmin):
    list_filter = ("categoria","proveedor")
    list_display = ('proveedor','categoria','margen_deseado')
    list_editable = ('margen_deseado',)

admin.site.register(Proveedor,ProveedorAdmin)
admin.site.register(MargenProvedor,MargenProveedorAdmin)

