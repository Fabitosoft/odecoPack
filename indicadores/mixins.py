import json

from braces.views import JSONResponseMixin
from django.db.models import Q
from django.db.models import Sum, Count
from django.utils import timezone

from biable.models import VendedorBiable, MovimientoVentaBiable
from cotizaciones.models import Cotizacion
from usuarios.models import Colaborador


class IndicadorMesMixin(JSONResponseMixin, object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user

        try:
            subalternos = Colaborador.objects.get(usuario__user=usuario).subalternos.all()
        except Colaborador.DoesNotExist:
            subalternos = None

        vendedores_biable = VendedorBiable.objects.select_related('colaborador__usuario__user').filter(
            Q(colaborador__in=subalternos) &
            ~Q(colaborador__usuario__user=usuario)
        )

        vendedor_usuario = VendedorBiable.objects.select_related('colaborador__usuario__user').filter(
            colaborador__usuario__user=usuario)

        print(vendedor_usuario)

        fecha_hoy = timezone.localtime(timezone.now()).date()
        day = fecha_hoy.day  # 5
        year = fecha_hoy.year  # 2016
        month = fecha_hoy.month  # 12

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

        indicadores_vendedores = []
        # Indicadores de Venta
        for vendedor in vendedores_biable:
            indicadores_vendedores.append(self.consulta(year, month, day, vendedor=vendedor))
        indicadores_vendedores.append(self.consulta(year, month, day, usuario_sesion=vendedor_usuario))
        # for venta in qsVentasMes:
        #     qsVentasDia = qsVentasMes.filter(day=day)

        # facturacion_ventas_mes = 0
        # cantidad_venta_mes = 0
        # facturacion_ventas_dia = 0
        # cantidad_venta_dia = 0
        # if qsVentasMes.exists():
        #     facturacion_ventas_mes = float(qsVentasMes[0]['fact_neta'])
        #     cantidad_venta_mes = float(qsVentasMes[0]['cantidad'])
        # if qsVentasDia.exists():
        #     facturacion_ventas_dia = float(qsVentasDia[0]['fact_neta'])
        #     cantidad_venta_dia = float(qsVentasDia[0]['cantidad'])
        #
        # # Indicadores Cotizaciones
        # facturacion_cotizaciones_mes = 0
        # cantidad_cotizaciones_mes = 0
        # facturacion_cotizaciones_dia = 0
        # cantidad_cotizaciones_dia = 0
        #
        # if qsCotizacionesMes.exists():
        #     facturacion_cotizaciones_mes = float(qsCotizacionesMes[0]['valor'])
        #     cantidad_cotizaciones_mes = float(qsCotizacionesMes[0]['cantidad'])
        # if qsCotizacionesDia.exists():
        #     facturacion_cotizaciones_dia = float(qsCotizacionesDia[0]['valor'])
        #     cantidad_cotizaciones_dia = float(qsCotizacionesDia[0]['cantidad'])
        #
        # if facturacion_cotizaciones_mes > 0:
        #     tasa_conversion_ventas_mes = (facturacion_ventas_mes / facturacion_cotizaciones_mes) * 100
        # else:
        #     tasa_conversion_ventas_mes = 0
        #
        # indicadores = {
        #     'facturacion_venta_mes': facturacion_ventas_mes,
        #     'facturacion_venta_dia': facturacion_ventas_dia,
        #     'cantidad_venta_mes': cantidad_venta_mes,
        #     'cantidad_venta_dia': cantidad_venta_dia,
        #     'valor_cotizacion_mes': facturacion_cotizaciones_mes,
        #     'valor_cotizacion_dia': facturacion_cotizaciones_dia,
        #     'cantidad_cotizaciones_mes': cantidad_cotizaciones_mes,
        #     'cantidad_cotizaciones_dia': cantidad_cotizaciones_dia,
        #     'tasa_conversion_ventas_mes': tasa_conversion_ventas_mes,
        # }
        #
        context['indicadores_venta'] = indicadores_vendedores
        return context

    def consulta(self, year, month, day, vendedor=None, usuario_sesion=[]):
        facturacion_ventas_mes = 0
        cantidad_venta_mes = 0
        facturacion_ventas_dia = 0
        cantidad_venta_dia = 0

        # Indicadores Cotizaciones
        facturacion_cotizaciones_mes = 0
        cantidad_cotizaciones_mes = 0
        facturacion_cotizaciones_dia = 0
        cantidad_cotizaciones_dia = 0

        qsVentasMes = MovimientoVentaBiable.objects.select_related(
            'vendedor__colaborador__usuario__user'
        ).values(
            'vendedor__colaborador__usuario__user'
        ).annotate(
            fact_neta=Sum('venta_neto'),
            cantidad=Count('nro_documento', 'tipo_documento')
        ).filter(
            Q(year=year) &
            Q(month=month) &
            (
                Q(vendedor=vendedor) |
                Q(vendedor__in=usuario_sesion)
            )
        )

        print(qsVentasMes)

        if qsVentasMes.exists():
            facturacion_ventas_mes = float(qsVentasMes[0]['fact_neta'])
            cantidad_venta_mes = float(qsVentasMes[0]['cantidad'])

        qsVentasDia = qsVentasMes.filter(day=day)

        if qsVentasDia.exists():
            facturacion_ventas_dia = float(qsVentasDia[0]['fact_neta'])
            cantidad_venta_dia = float(qsVentasDia[0]['cantidad'])

        qsCotizacionesMes = Cotizacion.objects.values('usuario').annotate(
            valor=Sum('total'),
            cantidad=Count('id')
        ).filter(
            Q(fecha_envio__month=month) &
            Q(fecha_envio__year=year) &
            (
                Q(usuario__user_extendido__colaborador__mi_vendedor_biable=vendedor) |
                Q(usuario__user_extendido__colaborador__mi_vendedor_biable__in=usuario_sesion)
            )
        )

        if qsCotizacionesMes.exists():
            facturacion_cotizaciones_mes = float(qsCotizacionesMes[0]['valor'])
            cantidad_cotizaciones_mes = float(qsCotizacionesMes[0]['cantidad'])

        qsCotizacionesDia = qsCotizacionesMes.filter(fecha_envio__day=day)

        if qsCotizacionesDia.exists():
            facturacion_cotizaciones_dia = float(qsCotizacionesDia[0]['valor'])
            cantidad_cotizaciones_dia = float(qsCotizacionesDia[0]['cantidad'])

        if facturacion_cotizaciones_mes > 0:
            tasa_conversion_ventas_mes = (facturacion_ventas_mes / facturacion_cotizaciones_mes) * 100
        else:
            tasa_conversion_ventas_mes = 0

        if vendedor:
            nombre = vendedor.colaborador.usuario.user.get_full_name()
        else:
            nombre = "Mi Indicador"

        indicador = {
            'nombre': nombre,
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

        return indicador
