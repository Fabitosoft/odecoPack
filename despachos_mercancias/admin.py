from django.contrib import admin

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
        'tipo',
        'forma_pago',
        'nro_tracking',
        'cliente',
        'servicio_boom',
        'rr'
    )
    list_filter = ('estado','servicio_boom','rr')
    search_fields = ('cliente__nombre','cliente_alternativo')
    raw_id_fields = ('cliente',)
    inlines = (FacturasBiableInline,)
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
                    ('servicio_boom', 'rr'),
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
