from django.contrib import admin

from .models import Cotizacion, ItemCotizacion, RemisionCotizacion


# Register your models here.

class ListaPrecioInline(admin.TabularInline):
    model = ItemCotizacion

    def user_email(self, instance):
        return instance.item

    fields = \
        (
            'get_nombre_item',
            "cantidad",
            "forma_pago",
            "precio",
            "total",
        )

    extra = 0
    readonly_fields = \
        (
            "cantidad",
            "precio",
            "forma_pago",
            "total",
            "get_nombre_item"
        )
    can_delete = False

class RemisionInline(admin.TabularInline):
    model = RemisionCotizacion

    fields = \
        (
            'nro_remision',
            "nro_factura",
            "fecha_prometida_entrega",
            "entregado"
        )

    extra = 0
    # readonly_fields = \
    #     (
    #         'nro_remision',
    #         "nro_factura",
    #         "fecha_prometida_entrega",
    #         "entregado"
    #     )

    #can_delete = False


class CotizacionAdmin(admin.ModelAdmin):
    list_display = ('estado', 'razon_social', 'modified', 'usuario')
    readonly_fields = ('total',)
    inlines = [
        ListaPrecioInline,
        RemisionInline,
    ]


admin.site.register(Cotizacion, CotizacionAdmin)
