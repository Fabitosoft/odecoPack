from django.db.models import Case, Sum, Value, When, DecimalField
from django.db.models import Q
from django.views.generic import TemplateView

from biable.models import FacturasBiable


# Create your views here.
class VistaPrueba(TemplateView):
    template_name = 'reportes_ventas/base_reporte_ventas.html'

    def get_context_data(self, **kwargs):
        print("entro a la vista")

        ano_entrada = 2017
        ano_1 = ano_entrada - 1
        ano_2 = ano_entrada - 2
        ano_3 = ano_entrada - 3

        qs = FacturasBiable.objects.values(
            'cliente_id'
        ).annotate(
            fact_t=Case(
                When(fecha_documento__year=ano_entrada,
                     then=Sum('venta_neto')),
                default=Value(0),
                output_field=DecimalField(),
            ),
            fact_t_1=Case(
                When(fecha_documento__year=ano_1,
                     then=Sum('venta_neto')),
                default=Value(0),
                output_field=DecimalField(),
            ),
            fact_t_2=Case(
                When(fecha_documento__year=ano_2,
                     then=Sum('venta_neto')),
                default=Value(0),
                output_field=DecimalField(),
            ),
            fact_t_3=Case(
                When(fecha_documento__year=ano_3,
                     then=Sum('venta_neto')),
                default=Value(0),
                output_field=DecimalField(),
            ),
        ).filter(
            Q(fecha_documento__year__gte=ano_3) &
            Q(fecha_documento__year__lte=ano_entrada) &
            Q(activa=True)
        )

        context = super().get_context_data(**kwargs)
        context['facturacion'] = qs

        return context
