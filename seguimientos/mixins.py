from .models import SeguimientoComercialCliente


class SeguimientoGestionComercialMixin(object):
    def get_seguimiento_comercial(self, nro_registros, cliente_pk=None, usuario_pk=None, tipo=None):
        qs = SeguimientoComercialCliente.objects.select_related(
            'cliente',
            'creado_por',
            'cotizacion',
            'cotizacion__cliente_biable',
            'comentario_cotizacion',
            'comentario_cotizacion',
            'comentario_cotizacion__cotizacion',
            'seguimiento_cliente',
            'seguimiento_cartera__tarea',
            'seguimiento_cartera__tarea__factura',
            'seguimiento_envio_tcc',
            'seguimiento_envio_tcc__tarea',
            'seguimiento_envio_tcc__tarea__envio',
            'seguimiento_cotizacion',
            'seguimiento_cotizacion__tarea',
            'seguimiento_cotizacion__tarea__cotizacion',
            'contacto',
        )
        if usuario_pk:
            qs = qs.filter(creado_por__pk=usuario_pk)
        if cliente_pk:
            qs = qs.filter(cliente__pk=cliente_pk)

        if tipo:
            if tipo == 'seguimiento_cotizacion':
                qs = qs.filter(seguimiento_cotizacion__isnull=False)
            elif tipo == 'seguimiento_cartera':
                qs = qs.filter(seguimiento_cartera__isnull=False)
            elif tipo == 'seguimiento_tcc':
                qs = qs.filter(seguimiento_envio_tcc__isnull=False)
            elif tipo == 'contactos':
                qs = qs.filter(contacto__isnull=False)
            elif tipo == 'seguimiento_cliente':
                qs = qs.filter(seguimiento_cliente__isnull=False)
            elif tipo == 'comentario_cotizacion':
                qs = qs.filter(comentario_cotizacion__isnull=False)
            elif tipo == 'cotizacion':
                qs = qs.filter(cotizacion__isnull=False)

        qs = qs.order_by('-created')

        if nro_registros:
            qs = qs[:nro_registros]
        return qs
