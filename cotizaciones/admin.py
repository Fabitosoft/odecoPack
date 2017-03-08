from django.contrib import admin
from django.contrib.admin import DateFieldListFilter

from .models import Cotizacion, ItemCotizacion, RemisionCotizacion, TareaCotizacion


# Register your models here.

class ListaPrecioInline(admin.TabularInline):
    model = ItemCotizacion

    def user_email(self, instance):
        return instance.item

    fields = (
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

    fields = (
        'tipo_remision',
        'nro_remision',
        "factura_biable",
        "fecha_prometida_entrega",
        "entregado"
    )
    raw_id_fields = ('factura_biable',)
    extra = 0


class TareasInline(admin.TabularInline):
    model = TareaCotizacion

    fields = (
        'nombre',
        "descripcion",
        "fecha_inicial",
        "fecha_final",
        "esta_finalizada",
    )

    extra = 0
    # readonly_fields = \
    #     (
    #         'nro_remision',
    #         "nro_factura",
    #         "fecha_prometida_entrega",
    #         "entregado"
    #     )

    # can_delete = False


class CotizacionAdmin(admin.ModelAdmin):
    list_select_related = [
        'cliente_biable',
        'ciudad_despacho',
        'usuario',
        'contacto',
        'cliente_biable',
        'ciudad_despacho__departamento',
        'ciudad_despacho__departamento__pais'
    ]
    list_display = (
        'nro_cotizacion',
        'estado',
        'razon_social',
        'modified',
        'usuario',
        'ciudad_despacho',
        'ciudad',
        'pais',
        'cliente_biable',
        'cliente_nuevo',
        'otra_ciudad',
        'sucursal_sub_empresa',
        'contacto'
    )
    readonly_fields = ('total',)
    list_editable = ('cliente_biable', 'contacto')
    raw_id_fields = ('cliente_biable', 'ciudad_despacho', 'contacto')
    list_filter = (
        'estado',
        'cliente_nuevo',
        'otra_ciudad',
        ('fecha_envio', DateFieldListFilter)
    )
    inlines = [
        ListaPrecioInline,
        RemisionInline,
        TareasInline,
    ]
    search_fields = (
        'pais',
        'ciudad',
        'razon_social',
        'estado',
        'nro_cotizacion',
        'cliente_biable__nombre',
        'cliente_biable__nit',
        'contacto__nombres',
        'contacto__apellidos'
    )


admin.site.register(Cotizacion, CotizacionAdmin)
