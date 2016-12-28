from django.contrib import admin

from biable.models import VendedorBiable, VendedorBiableUser, LineaVendedorBiable
# Register your models here.

class VendedorBiableAdmin(admin.ModelAdmin):
    list_display = ('nombre','id')

admin.site.register(VendedorBiable,VendedorBiableAdmin)
admin.site.register(VendedorBiableUser)
admin.site.register(LineaVendedorBiable)
