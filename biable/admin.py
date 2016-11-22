from django.contrib import admin

from biable.models import VendedorBiable
# Register your models here.

class VendedorBiableAdmin(admin.ModelAdmin):
    list_display = ('nombre','id','linea')

admin.site.register(VendedorBiable,VendedorBiableAdmin)
