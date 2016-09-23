from django.contrib import admin

from .models import Cotizacion, ItemCotizacion
# Register your models here.

class ListaPrecioInline(admin.TabularInline):
    model = ItemCotizacion
    extra = 0
    #readonly_fields = ('myclasssummary',)
    can_delete = False

class CotizacionAdmin(admin.ModelAdmin):
    list_display = ('estado', 'razon_social','modified')

    inlines = [
        ListaPrecioInline,
    ]

admin.site.register(Cotizacion,CotizacionAdmin)