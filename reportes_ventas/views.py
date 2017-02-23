from django.db.models import Case, Sum, Value, When, DecimalField
from django.db.models import Q
from django.views.generic import TemplateView

from .models import HistoricoVenta


# Create your views here.
class VistaPrueba(TemplateView):
    template_name = 'reportes_ventas/base_reporte_ventas.html'

    def get_context_data(self, **kwargs):
        qs = HistoricoVenta.objects.values(
            'cliente__nombre',
            'vendedor__linea_ventas__nombre'
        ).annotate(
            # creci=(Sum('t_1_venta_neta')-Sum('t_venta_neta'))/(Sum('t_1_venta_neta')),
            fact_t=Sum('t_venta_neta'),
            fact_t_1=Sum('t_1_venta_neta'),
            fact_t_2=Sum('t_2_venta_neta'),
            fact_t_3=Sum('t_3_venta_neta'),
            fact_t_acum=Sum('t_venta_neta_acum'),
            fact_t_1_acum=Sum('t_1_venta_neta_acum'),
            fact_t_2_acum=Sum('t_2_venta_neta_acum'),
            fact_t_3_acum=Sum('t_3_venta_neta_acum'),
        ).order_by('vendedor__linea_ventas__nombre')
        context = super().get_context_data(**kwargs)
        context['facturacion'] = qs

        return context
