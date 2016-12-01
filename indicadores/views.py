from django.db.models import Case, CharField, Sum, Max, Min, Count, When, F
from django.db.models import Value
from django.utils import timezone
from django.views.generic import TemplateView

from braces.views import JSONResponseMixin, AjaxResponseMixin

from biable.models import MovimientoVentaBiable


# Create your views here.
class VentasVendedor(JSONResponseMixin, AjaxResponseMixin, TemplateView):
    template_name = 'indicadores/ventasxvendedor.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ano_fin = MovimientoVentaBiable.objects.all().aggregate(Max('year'))['year__max']
        ano_ini = MovimientoVentaBiable.objects.all().aggregate(Min('year'))['year__min']
        ano_fin = ano_fin + 1

        context['anos_list'] = list(range(ano_ini, ano_fin))

        return context

    def post_ajax(self, request, *args, **kwargs):
        ano = self.request.POST.getlist('anos[]')
        mes = self.request.POST.getlist('meses[]')

        qs = self.consulta(ano, mes)
        lista = list(qs)
        for i in lista:
            i["v_bruta"] = int(i["v_bruta"])
            i["Costo"] = int(i["Costo"])
            i["v_neto"] = int(i["v_neto"])
            i["renta"] = int(i["renta"])
            i["Descuentos"] = int(i["Descuentos"])
        return self.render_json_response(lista)

    def consulta(self, ano, mes):
        qs = MovimientoVentaBiable.objects.all().values('vendedor__nombre').annotate(
            vendedor_nombre=F('vendedor__nombre'),
            v_bruta=Sum('venta_bruta'),
            v_neto=Sum('venta_neto'),
            Descuentos=Sum('dscto_netos'),
            Costo=Sum('costo_total'),
            renta=Sum('rentabilidad'),
            Margen=(Sum('rentabilidad') / Sum('venta_bruta') * 100),
            linea=Case(
                When(vendedor__linea=1, then=Value('Proyectos')),
                When(vendedor__linea=2, then=Value('Bandas y Componentes')),
                default=Value('Posventa'),
                output_field=CharField(),
            ),
        ).filter(year__in=list(map(lambda x: int(x), ano)), month__in=list(map(lambda x: int(x), mes)))
        print(qs.all().count())
        return qs

class VentasClientes(JSONResponseMixin, AjaxResponseMixin, TemplateView):
    template_name = 'indicadores/ventasxcliente.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ano_fin = MovimientoVentaBiable.objects.all().aggregate(Max('year'))['year__max']
        ano_ini = MovimientoVentaBiable.objects.all().aggregate(Min('year'))['year__min']
        ano_fin = ano_fin + 1

        context['anos_list'] = list(range(ano_ini, ano_fin))

        return context

    def post_ajax(self, request, *args, **kwargs):
        ano = self.request.POST.getlist('anos[]')
        mes = self.request.POST.getlist('meses[]')
        linea = self.request.POST.get('linea')

        qs = self.consulta(ano, mes)

        if not linea == "0":
            qs = qs.filter(vendedor__linea=linea)

        lista = list(qs)
        for i in lista:
            i["v_bruta"] = int(i["v_bruta"])
            i["Costo"] = int(i["Costo"])
            i["v_neto"] = int(i["v_neto"])
            i["renta"] = int(i["renta"])
            i["Descuentos"] = int(i["Descuentos"])
        return self.render_json_response(lista)

    def consulta(self, ano, mes):
        qs = MovimientoVentaBiable.objects.all().values('cliente').annotate(
            v_bruta=Sum('venta_bruta'),
            v_neto=Sum('venta_neto'),
            Descuentos=Sum('dscto_netos'),
            Costo=Sum('costo_total'),
            renta=Sum('rentabilidad'),
            Margen=(Sum('rentabilidad') / Sum('venta_bruta') * 100),
            linea=Case(
                When(vendedor__linea=1, then=Value('Proyectos')),
                When(vendedor__linea=2, then=Value('Bandas y Componentes')),
                default=Value('Posventa'),
                output_field=CharField(),
            ),
        ).filter(
            year__in=list(map(lambda x: int(x), ano)),
            month__in=list(map(lambda x: int(x), mes))
        ).order_by('-v_bruta')
        print(qs.all().count())
        return qs


class VentasClientesAno(JSONResponseMixin, AjaxResponseMixin, TemplateView):
    template_name = 'indicadores/ventasxclientexano.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ano_fin = MovimientoVentaBiable.objects.all().aggregate(Max('year'))['year__max']
        ano_ini = MovimientoVentaBiable.objects.all().aggregate(Min('year'))['year__min']
        ano_fin = ano_fin + 1

        context['anos_list'] = list(range(ano_ini, ano_fin))

        return context

    def post_ajax(self, request, *args, **kwargs):
        ano = self.request.POST.getlist('anos[]')
        mes = self.request.POST.getlist('meses[]')
        linea = self.request.POST.get('linea')

        qs = self.consulta(ano, mes)

        if not linea == "0":
            qs = qs.filter(vendedor__linea=linea)

        lista = list(qs)
        for i in lista:
            i["v_bruta"] = int(i["v_bruta"])
            i["Costo"] = int(i["Costo"])
            i["v_neto"] = int(i["v_neto"])
            i["renta"] = int(i["renta"])
            i["Descuentos"] = int(i["Descuentos"])
        return self.render_json_response(lista)

    def consulta(self, ano, mes):
        qs = MovimientoVentaBiable.objects.all().values('cliente', 'year').annotate(
            v_bruta=Sum('venta_bruta'),
            v_neto=Sum('venta_neto'),
            Descuentos=Sum('dscto_netos'),
            Costo=Sum('costo_total'),
            renta=Sum('rentabilidad'),
            Margen=(Sum('rentabilidad') / Sum('venta_bruta') * 100),
            linea=Case(
                When(vendedor__linea=1, then=Value('Proyectos')),
                When(vendedor__linea=2, then=Value('Bandas y Componentes')),
                default=Value('Posventa'),
                output_field=CharField(),
            ),
        ).filter(
            year__in=list(map(lambda x: int(x), ano)),
            month__in=list(map(lambda x: int(x), mes))
        ).order_by('-v_bruta')
        print(qs.all().count())
        print(qs)
        return qs


class FacturacionAno(JSONResponseMixin, AjaxResponseMixin, TemplateView):
    template_name = 'indicadores/facturacionxano.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ano_fin = MovimientoVentaBiable.objects.all().aggregate(Max('year'))['year__max']
        ano_ini = MovimientoVentaBiable.objects.all().aggregate(Min('year'))['year__min']
        ano_fin = ano_fin + 1

        context['anos_list'] = list(range(ano_ini, ano_fin))
        return context

    def post_ajax(self, request, *args, **kwargs):
        ano = self.request.POST.get('ano')
        linea = self.request.POST.get('linea')
        qs = self.consulta(ano)

        if not linea == "0":
            print('entro')
            qs = qs.filter(vendedor__linea=linea)

        print(qs.all().count())

        lista = list(qs)
        for i in lista:
            i["v_bruta"] = int(i["v_bruta"])
            i["Costo"] = int(i["Costo"])
            i["v_neto"] = int(i["v_neto"])
            i["renta"] = int(i["renta"])
            i["Descuentos"] = int(i["Descuentos"])
            i["Impuestos"] = int(i["Impuestos"])
        return self.render_json_response(lista)

    def consulta(self, ano):
        qs = MovimientoVentaBiable.objects.values('month').annotate(
            v_bruta=Sum('venta_bruta'),
            v_neto=Sum('venta_neto'),
            Descuentos=Sum('dscto_netos'),
            Costo=Sum('costo_total'),
            renta=Sum('rentabilidad'),
            Impuestos=Sum('imp_netos'),
            Margen=(Sum('rentabilidad') / Sum('venta_bruta') * 100)
        ).filter(year=ano).order_by('month')
        return qs


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
            Margen=(Sum('rentabilidad') / Sum('venta_neto') * 100)
        ).filter(year=ano)

        return context