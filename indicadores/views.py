import numpy as np

from django.db.models import Sum, Max, Min, Count
from django.db.models import F
from django.utils import timezone
from django.views.generic import TemplateView
# import pandas as pd
# from pandas import pivot_table

from biable.models import MovimientoVentaBiable, VendedorBiable


# Create your views here.
class VentasVendedor(TemplateView):
    template_name = 'indicadores/ventasxvendedor.html'

    def get_context_data(self, **kwargs):
        hoy = timezone.now()
        mes = [hoy.month]
        ano = hoy.year

        if self.request.GET.get('ano'):
            ano = self.request.GET.get('ano')

        if self.request.GET.get('mes'):
            mes = self.request.GET.getlist('mes')

        context = super().get_context_data(**kwargs)

        ano_fin = MovimientoVentaBiable.objects.all().aggregate(Max('year'))['year__max']
        ano_ini = MovimientoVentaBiable.objects.all().aggregate(Min('year'))['year__min']
        ano_fin = ano_fin + 1

        context['anos_list'] = list(range(ano_ini, ano_fin))

        qs = MovimientoVentaBiable.objects.all().values('vendedor').annotate(
            vendedor_nombre=F('vendedor__nombre'),
            v_bruta=Sum('venta_bruta'),
            v_neto=Sum('venta_neto'),
            Descuentos=Sum('dscto_netos'),
            Costo=Sum('costo_total'),
            renta=Sum('rentabilidad')
        ).filter(year=ano, month__in=mes)



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


class FacturacionAno(TemplateView):
    template_name = 'indicadores/facturacionxano.html'

    def get_context_data(self, **kwargs):
        hoy = timezone.now()
        ano = hoy.year

        if self.request.GET.get('ano'):
            ano = self.request.GET.get('ano')

        context = super().get_context_data(**kwargs)

        ano_fin = MovimientoVentaBiable.objects.all().aggregate(Max('year'))['year__max']
        ano_ini = MovimientoVentaBiable.objects.all().aggregate(Min('year'))['year__min']
        ano_fin = ano_fin + 1

        context['anos_list'] = list(range(ano_ini, ano_fin))

        qs = MovimientoVentaBiable.objects.values('month').annotate(
            v_bruta=Sum('venta_bruta'),
            v_neto=Sum('venta_neto'),
            Descuentos=Sum('dscto_netos'),
            Costo=Sum('costo_total'),
            renta=Sum('rentabilidad'),
            Margen = (Sum('rentabilidad') / Sum('venta_neto') * 100)
        ).filter(year=ano)


        # if qs.exists():
        #     print(qs.all().count())
        #     df = pd.DataFrame.from_records(qs)
        #     #df[['v_neto', 'v_bruta']].apply(pd.to_numeric)
        #     df[['v_neto', 'v_bruta']].apply(lambda x: pd.to_numeric(x, errors='ignore'))
        #
        #     print(df)
        #
        #     df.rename(
        #         columns={
        #             'month': 'Mes',
        #             'renta': 'Rent.',
        #             'v_neto': 'Vr. Neto.',
        #             'v_bruta': 'Vr. Bruto.',
        #         },
        #         inplace=True)
        #
        #     table = pivot_table(df,
        #                         values=['Vr. Bruto.', 'Descuentos', 'Vr. Neto.', 'Costo', 'Rent.','Margen'],
        #                         columns=['Mes'],
        #                         aggfunc=np.sum,
        #                         fill_value=0,
        #                         dropna=True
        #                         )
        #
        #     tableF = table.reindex_axis(['Vr. Bruto.', 'Descuentos', 'Vr. Neto.', 'Costo', 'Rent.', 'Margen'], axis=0)
        #
        #     context['tabla_consulta'] = tableF.to_html(classes="table table-striped")
        #     context['ano_filtro'] = ano

        return context


class FacturacionAnoLinea(TemplateView):
    template_name = 'indicadores/facturacionxanoxlinea.html'

    def get_context_data(self, **kwargs):
        hoy = timezone.now()
        ano = hoy.year

        if self.request.GET.get('ano'):
            ano = self.request.GET.get('ano')

        context = super().get_context_data(**kwargs)

        ano_fin = MovimientoVentaBiable.objects.all().aggregate(Max('year'))['year__max']
        ano_ini = MovimientoVentaBiable.objects.all().aggregate(Min('year'))['year__min']
        ano_fin = ano_fin + 1

        context['anos_list'] = list(range(ano_ini, ano_fin))


        qs = MovimientoVentaBiable.objects.values('month').annotate(
            v_bruta=Sum('venta_bruta'),
            v_neto=Sum('venta_neto'),
            Descuentos=Sum('dscto_netos'),
            Costo=Sum('costo_total'),
            renta=Sum('rentabilidad'),
            Margen = (Sum('rentabilidad') / Sum('venta_neto') * 100)
        ).filter(year=ano)


        # if qs.exists():
        #     print(qs.all().count())
        #     df = pd.DataFrame.from_records(qs)
        #     #df[['v_neto', 'v_bruta']].apply(pd.to_numeric)
        #     df[['v_neto', 'v_bruta']].apply(lambda x: pd.to_numeric(x, errors='ignore'))
        #
        #     print(df)
        #
        #     df.rename(
        #         columns={
        #             'month': 'Mes',
        #             'renta': 'Rent.',
        #             'v_neto': 'Vr. Neto.',
        #             'v_bruta': 'Vr. Bruto.',
        #         },
        #         inplace=True)
        #
        #     table = pivot_table(df,
        #                         values=['Vr. Bruto.', 'Descuentos', 'Vr. Neto.', 'Costo', 'Rent.','Margen'],
        #                         columns=['Mes'],
        #                         aggfunc=np.sum,
        #                         fill_value=0,
        #                         dropna=True
        #                         )
        #
        #     tableF = table.reindex_axis(['Vr. Bruto.', 'Descuentos', 'Vr. Neto.', 'Costo', 'Rent.', 'Margen'], axis=0)
        #
        #     context['tabla_consulta'] = tableF.to_html(classes="table table-striped")
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
