from django.contrib import admin

from import_export.admin import ImportExportModelAdmin

from proveedores.models import Proveedor
# Register your models here.

class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'moneda')

admin.site.register(Proveedor,ProveedorAdmin)

