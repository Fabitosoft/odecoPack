import numpy as np

from django.db.models import Sum, Max, Min
from django.db.models import F
from django.utils import timezone
from django.db.models.functions import TruncMonth, TruncYear
from django.views.generic import TemplateView
#import pandas as pd
#from pandas import pivot_table

from biable.models import MovimientoVentaBiable


# Create your views here.
class VentasVendedor(TemplateView):
    template_name = 'indicadores/ventasxvendedor.html'

    def get_context_data(self, **kwargs):
        hoy = timezone.now()
        mes = [hoy.month]
        ano = hoy.year

        if self.request.GET.get('ano'):
            ano = self.request.GET.get('ano')
            print(ano)

        if self.request.GET.get('mes'):
            mes = self.request.GET.getlist('mes')
            print(mes)

        a = np.array([1, 2, 3])  # Create a rank 1 array
        print(type(a))

        context = super().get_context_data(**kwargs)
        ano_fin = MovimientoVentaBiable.objects.latest('fecha').fecha.year + 1
        ano_ini = MovimientoVentaBiable.objects.earliest('fecha').fecha.year

        context['anos_list'] = list(range(ano_ini, ano_fin))

        qs = MovimientoVentaBiable.objects.values('vendedor').annotate(
            vendedor_nombre=F('vendedor__nombre'),
            v_bruta=Sum('venta_bruta'),
            v_neto=Sum('venta_neto'),
            Descuentos=Sum('dscto_netos'),
            Costo=Sum('costo_total'),
            renta=Sum('rentabilidad')
        ).filter(fecha__year=ano, fecha__month__in=mes)

        # if qs.exists():
        #     df = pd.DataFrame.from_records(qs)
        #     print(qs)
        #     print(df)
        #     print(df.dtypes)
        #     #df[['v_neto', 'v_bruta']].apply(pd.to_numeric)
        #     df[['v_neto', 'v_bruta']].apply(lambda x: pd.to_numeric(x, errors='ignore'))
        #
        #     df.rename(
        #         columns={
        #             'vendedor_nombre': 'Vendedor',
        #             'ano': 'Año',
        #             'renta': 'Rent.',
        #             'v_neto': 'Vr. Neto.',
        #             'v_bruta': 'Vr. Bruto.',
        #         },
        #         inplace=True)
        #
        #     table = pivot_table(df,
        #                         index=['Vendedor'],
        #                         values=['Vr. Bruto.', 'Descuentos', 'Vr. Neto.', 'Costo', 'Rent.'],
        #                         aggfunc=np.sum,
        #                         fill_value=0,
        #                         dropna=True
        #                         )
        #
        #     table['margen'] = (table['Rent.'] / table['Vr. Neto.']) * 100
        #
        #     table.sort_values('Vr. Bruto.', ascending=False, inplace=True)
        #
        #     tableF = table.reindex_axis(['Vr. Bruto.', 'Descuentos', 'Vr. Neto.', 'Costo', 'Rent.', 'margen'], axis=1)
        #
        #     context['tabla_consulta'] = tableF.to_html(classes="table table-striped")
        #     context['meses_filtro'] = mes
        #     context['ano_filtro'] = ano

        return context

        # # Create your views here.
        # class VentasVendedor(TemplateView):
        #     template_name = 'indicadores/ventasxvendedor.html'
        #
        #     def get_context_data(self, **kwargs):
        #         context = super().get_context_data(**kwargs)
        #         qs = MovimientoVentaBiable.objects.values('vendedor').annotate(
        #             mes=TruncMonth('fecha'),
        #             ano=TruncYear('fecha'),
        #             vendedor_nombre=F('vendedor__nombre'),
        #             renta=Sum('rentabilidad'),
        #             v_neto=Sum('venta_neto')
        #         )
        #         # pd.options.display.float_format = '${:,.2f}'.format
        #         # df['cost'] = df['cost'].map('${:,.2f}'.format)ss
        #
        #         # output = df.to_html(formatters={
        #         #     'var1': '{:,.2f}'.format,
        #         #     'var2': '{:,.2f}'.format,
        #         #     'var3': '{:,.2%}'.format
        #         # })
        #
        #         print(qs.all().count())
        #
        #
        #         df = pd.DataFrame.from_records(qs)
        #
        #         df['mes'] = df['mes'].dt.month
        #         df['ano'] = df['ano'].dt.year
        #
        #         df.rename(
        #             columns={
        #                 'vendedor_nombre': 'Vendedor',
        #                 'ano': 'Año',
        #                 'mes': 'Mes',
        #                 'renta': 'Rent.',
        #                 'v_neto': 'Vr. Neto.',
        #             },
        #             inplace=True)
        #
        #
        #         table = pivot_table(df,
        #                             index=['Vendedor', 'Mes'],
        #                             values=['Rent.', 'Vr. Neto.'],
        #                             columns=['Año'],
        #                             aggfunc={'Vr. Neto.': np.sum, 'Rent.': np.sum},
        #                             fill_value=0,
        #                             dropna=True
        #                             )
        #         #table['margen'] = (table['Rent.'] / table['Vr. Neto.']) * 100
        #
        #         context['tabla_consulta'] = table.to_html(classes="table table-striped")
        #         return context
