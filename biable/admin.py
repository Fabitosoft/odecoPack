from django.contrib import admin

from biable.models import VendedorBiable
# Register your models here.

class VendedorBiableAdmin(admin.ModelAdmin):
    list_display = ('id','nombre','linea')

admin.site.register(VendedorBiable,VendedorBiableAdmin)
