from django.contrib import admin

from biable.models import VendedorBiable, VendedorBiableUser
# Register your models here.

class VendedorBiableAdmin(admin.ModelAdmin):
    list_display = ('nombre','id','linea')
    list_editable = ('linea')

admin.site.register(VendedorBiable,VendedorBiableAdmin)
admin.site.register(VendedorBiableUser)
