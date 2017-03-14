from biable.models import (
    LineaVendedorBiable,
    Actualizacion,
    FacturasBiable
)


class InformeVentasConLineaMixin(object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lineas_list'] = LineaVendedorBiable.objects.all()
        return context


class InformeVentasConAnoMixin(object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ano_fin = FacturasBiable.objects.latest('fecha_documento').fecha_documento.year
        ano_ini = FacturasBiable.objects.earliest('fecha_documento').fecha_documento.year
        ano_fin = ano_fin + 1
        context['anos_list'] = list(range(ano_ini, ano_fin))
        return context


class FechaActualizacionMovimientoVentasMixin(object):
    def get_ultima_actualizacion(self, **kwargs):
        ultima_actualizacion = Actualizacion.tipos.movimiento_ventas()
        if ultima_actualizacion:
            ultima_actualizacion = ultima_actualizacion.latest('fecha')
            return ultima_actualizacion.fecha_formateada()
        return None
