from django.contrib import admin
from django.contrib.admin import DateFieldListFilter

from .models import EnvioTransportadoraTCC


# Register your models here.

class FacturasBiableInline(admin.TabularInline):
    model = EnvioTransportadoraTCC.facturas.through
    raw_id_fields = ('facturasbiable',)
    extra = 0


class EnvioTransportadoraTCCAdmin(admin.ModelAdmin):
    list_display = (
        'fecha_envio',
        'estado',
        'cliente',
        'tipo',
        'forma_pago',
        'nro_tracking',
        'fecha_entrega',
        'nro_tracking_boom',
        'fecha_entrega_boom',
    )
    list_filter = (
    'estado', ('fecha_envio', DateFieldListFilter), ('fecha_entrega', DateFieldListFilter),
    ('fecha_entrega_boom', DateFieldListFilter),)
    search_fields = ('cliente__nombre', 'cliente_alternativo','nro_tracking','nro_tracking_boom','estado','observacion',)
    raw_id_fields = ('cliente',)
    inlines = (FacturasBiableInline,)
    list_editable = ('estado', 'fecha_entrega', 'fecha_entrega_boom')
    fieldsets = (
        ('Informacion General', {
            'classes': ('form-control',),
            'fields':
                (
                    ('cliente', 'cliente_alternativo'),
                    'fecha_envio',
                    'nro_factura_transportadora',
                    ('tipo', 'forma_pago'),
                    'valor'
                )
        }),
        ('Seguimiento', {
            'classes': ('form-control',),
            'fields':
                (
                    ('nro_tracking',
                     'fecha_entrega'),
                    'estado',
                )
        }),
        ('Boom', {
            'classes': ('form-control',),
            'fields':
                (
                    ('nro_tracking_boom', 'fecha_entrega_boom'),
                )
        }),
        ('Observaciones', {
            'classes': ('form-control',),
            'fields':
                (
                    'observacion',
                )
        }),
    )


admin.site.register(EnvioTransportadoraTCC, EnvioTransportadoraTCCAdmin)
