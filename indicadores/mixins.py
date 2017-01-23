from django.db.models import Sum, Count
from django.utils import timezone

from biable.models import VendedorBiable, MovimientoVentaBiable
from cotizaciones.models import Cotizacion


class IndicadorMesMixin(object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        vendedores_biable = VendedorBiable.objects.filter(colaborador__usuario__user=usuario)

        if usuario.has_perm('trabajo_diario.ver_trabajo_diario'):
            fecha_hoy = timezone.localtime(timezone.now()).date()
            day = 5
            year = 2016  # fecha_hoy.year
            month = 12  # fecha_hoy.month
            usuario = self.request.user

            qsVentasMes = MovimientoVentaBiable.objects.values('vendedor__colaborador').annotate(
                fact_neta=Sum('venta_neto'),
                cantidad=Count('nro_documento', 'tipo_documento')
            ).filter(
                vendedor__in=vendedores_biable,
                year=year,
                month=month
            )
            qsVentasDia = qsVentasMes.filter(day=day)

            # qsClientesVentasMes = MovimientoVentaBiable.objects.values('factura__cliente').annotate(
            #     cantidad=Count('id_terc_fa')
            # ).filter(
            #     vendedor__in=vendedores_biable,
            #     year=year,
            #     month=month
            # )
            #
            # if qsClientesVentasMes.exists():
            #     print(qsClientesVentasMes[0])
            #
            # qsClientesCotizacionesMes = Cotizacion.objects.values('usuario').annotate(
            #     valor=Sum('total'),
            #     cantidad=Count('id')
            # ).filter(
            #     fecha_envio__month=month,
            #     fecha_envio__year=year,
            #     usuario=usuario
            # )
            #
            # if qsClientesCotizacionesMes.exists():
            #     print(qsClientesCotizacionesMes[0])

            qsCotizacionesMes = Cotizacion.objects.values('usuario').annotate(
                valor=Sum('total'),
                cantidad=Count('id')
            ).filter(
                fecha_envio__month=month,
                fecha_envio__year=year,
                usuario=usuario,
            )

            qsCotizacionesDia = qsCotizacionesMes.filter(fecha_envio__day=day)

            # Indicadores de Venta

            facturacion_ventas_mes = 0
            cantidad_venta_mes = 0
            facturacion_ventas_dia = 0
            cantidad_venta_dia = 0
            if qsVentasMes.exists():
                facturacion_ventas_mes = float(qsVentasMes[0]['fact_neta'])
                cantidad_venta_mes = float(qsVentasMes[0]['cantidad'])
            if qsVentasDia.exists():
                facturacion_ventas_dia = float(qsVentasDia[0]['fact_neta'])
                cantidad_venta_dia = float(qsVentasDia[0]['cantidad'])

            # Indicadores Cotizaciones
            facturacion_cotizaciones_mes = 0
            cantidad_cotizaciones_mes = 0
            facturacion_cotizaciones_dia = 0
            cantidad_cotizaciones_dia = 0

            if qsCotizacionesMes.exists():
                facturacion_cotizaciones_mes = float(qsCotizacionesMes[0]['valor'])
                cantidad_cotizaciones_mes = float(qsCotizacionesMes[0]['cantidad'])
            if qsCotizacionesDia.exists():
                facturacion_cotizaciones_dia = float(qsCotizacionesDia[0]['valor'])
                cantidad_cotizaciones_dia = float(qsCotizacionesDia[0]['cantidad'])

            if facturacion_ventas_mes > 0:
                tasa_conversion_ventas_mes = (facturacion_ventas_mes / facturacion_cotizaciones_mes)*100
            else:
                tasa_conversion_ventas_mes = 0

            indicadores = {
                'facturacion_venta_mes': facturacion_ventas_mes,
                'facturacion_venta_dia': facturacion_ventas_dia,
                'cantidad_venta_mes': cantidad_venta_mes,
                'cantidad_venta_dia': cantidad_venta_dia,
                'valor_cotizacion_mes': facturacion_cotizaciones_mes,
                'valor_cotizacion_dia': facturacion_cotizaciones_dia,
                'cantidad_cotizaciones_mes': cantidad_cotizaciones_mes,
                'cantidad_cotizaciones_dia': cantidad_cotizaciones_dia,
                'tasa_conversion_ventas_mes': tasa_conversion_ventas_mes,
            }

            context['indicadores'] = indicadores

        return context
