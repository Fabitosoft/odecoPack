from django.db.models import Case, CharField, Sum, Max, Min, Count, When, F
from django.db.models import Value
from django.db.models.functions import Concat
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from braces.views import JSONResponseMixin, AjaxResponseMixin

from biable.models import (
    MovimientoVentaBiable,
    VendedorBiableUser,
    Actualizacion
)


# from crm.models import VtigerCrmentity, VtigerAccountscf

# Create your views here.
class VentasVendedor(JSONResponseMixin, AjaxResponseMixin, TemplateView):
    template_name = 'indicadores/ventasxvendedor.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ano_fin = MovimientoVentaBiable.objects.all().aggregate(Max('year'))['year__max']
        ano_ini = MovimientoVentaBiable.objects.all().aggregate(Min('year'))['year__min']
        ano_fin = ano_fin + 1

        context['anos_list'] = list(range(ano_ini, ano_fin))
        # accounts_list = VtigerCrmentity.objects.using('biable').values('crmid').filter(smownerid__user_name='alalopros',
        #                                                                                setype='Accounts')
        # nits = VtigerAccountscf.objects.using('biable').values('cf_751').filter(accountid__in=accounts_list)
        # nits = list(nits)
        # nits_filtro = []
        # for nit in nits:
        #     nits_filtro.append(nit['cf_751'])
        # resultado = MovimientoVentaBiable.objects.filter(id_terc_fa__in=nits_filtro)
        # print(resultado)
        # print(nits)
        # list(accounts_list)
        return context

    def post_ajax(self, request, *args, **kwargs):
        ultima_actualizacion = Actualizacion.objects.filter(tipo='MOVIMIENTO_VENTAS').latest('fecha').fecha_formateada()
        context = {"fecha_actualizacion": ultima_actualizacion}

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
        context["lista"] = lista
        return self.render_json_response(context)

    def consulta(self, ano, mes):
        vendedores = VendedorBiableUser.objects.get(usuario__user=self.request.user).vendedores.all()
        qs = MovimientoVentaBiable.objects.all().values('vendedor__nombre').annotate(
            vendedor_nombre=F('vendedor__nombre'),
            v_bruta=Sum('venta_bruta'),
            v_neto=Sum('venta_neto'),
            Descuentos=Sum('dscto_netos'),
            Costo=Sum('costo_total'),
            renta=Sum('rentabilidad'),
            Margen=(Sum('rentabilidad') / Sum('venta_neto') * 100),
            linea=Case(
                When(vendedor__linea=1, then=Value('Proyectos')),
                When(vendedor__linea=2, then=Value('Bandas y Componentes')),
                default=Value('Posventa'),
                output_field=CharField(),
            ),
        ).filter(year__in=list(map(lambda x: int(x), ano)), month__in=list(map(lambda x: int(x), mes)),
                 vendedor__in=vendedores)
        print(qs.all().count())
        return qs


class VentasVendedorConsola(JSONResponseMixin, AjaxResponseMixin, TemplateView):
    template_name = 'indicadores/consolaxventasxvendedor.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ano_fin = MovimientoVentaBiable.objects.all().aggregate(Max('year'))['year__max']
        ano_ini = MovimientoVentaBiable.objects.all().aggregate(Min('year'))['year__min']
        ano_fin = ano_fin + 1

        context['anos_list'] = list(range(ano_ini, ano_fin))
        return context

    def post_ajax(self, request, *args, **kwargs):
        ultima_actualizacion = Actualizacion.objects.filter(tipo='MOVIMIENTO_VENTAS').latest('fecha').fecha_formateada()
        context = {"fecha_actualizacion": ultima_actualizacion}

        ano = self.request.POST.getlist('anos[]')
        mes = self.request.POST.getlist('meses[]')
        qs = self.consulta(ano, mes)
        lista = list(qs)

        for i in lista:
            i["v_neto"] = int(i["v_neto"])
        context["lista"] = lista
        return self.render_json_response(context)

    def consulta(self, ano, mes):
        usuario = get_object_or_404(VendedorBiableUser, usuario__user=self.request.user)
        qs = None
        if usuario.vendedores.all():
            qs = MovimientoVentaBiable.objects.all().values('day').annotate(
                vendedor_nombre=F('vendedor__nombre'),
                cliente=F('cliente'),
                documento=Concat('tipo_documento',Value('-'),'nro_documento'),
                tipo_documento = F('tipo_documento'),
                v_neto=Sum('venta_neto')
            ).filter(year__in=list(map(lambda x: int(x), ano)),
                     month__in=list(map(lambda x: int(x), mes)),
                     vendedor__in=usuario.vendedores.all()
                     ).order_by('day')
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
        ultima_actualizacion = Actualizacion.objects.filter(tipo='MOVIMIENTO_VENTAS').latest('fecha').fecha_formateada()
        context = {"fecha_actualizacion": ultima_actualizacion}
        ano = self.request.POST.getlist('anos[]')
        mes = self.request.POST.getlist('meses[]')
        linea = self.request.POST.get('linea')

        qs = self.consulta(ano, mes)

        if not linea == "0":
            qs = qs.filter(vendedor__linea=linea)

        total_fact = qs.aggregate(Sum('venta_neto'))["venta_neto__sum"]

        pareto = []
        sum = 0
        for cli in qs.values('id_terc_fa').annotate(fac=Sum('venta_neto')).order_by('-fac').all():
            sum += (int(cli['fac']) / total_fact) * 100
            if sum <= 80:
                pareto.append(cli['id_terc_fa'])

        qs = qs.annotate(tipo=Case(
            When(id_terc_fa__in=pareto,
                 then=Value('Pareto')),
            default=Value('Otros'),
            output_field=CharField(),
        )).order_by('-v_neto')

        lista = list(qs)
        for i in lista:
            i["v_bruta"] = int(i["v_bruta"])
            i["Costo"] = int(i["Costo"])
            i["v_neto"] = int(i["v_neto"])
            i["renta"] = int(i["renta"])
            i["Descuentos"] = int(i["Descuentos"])
        context["lista"] = lista
        return self.render_json_response(context)

    def consulta(self, ano, mes):
        qs = MovimientoVentaBiable.objects.all().values('cliente').annotate(
            v_bruta=Sum('venta_bruta'),
            v_neto=Sum('venta_neto'),
            Descuentos=Sum('dscto_netos'),
            Costo=Sum('costo_total'),
            renta=Sum('rentabilidad'),
            Margen=(Sum('rentabilidad') / Sum('venta_neto') * 100)
        ).filter(
            year__in=list(map(lambda x: int(x), ano)),
            month__in=list(map(lambda x: int(x), mes))
        )
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
        ultima_actualizacion = Actualizacion.objects.filter(tipo='MOVIMIENTO_VENTAS').latest('fecha').fecha_formateada()
        context = {"fecha_actualizacion": ultima_actualizacion}
        ano = self.request.POST.getlist('anos[]')
        mes = self.request.POST.getlist('meses[]')
        linea = self.request.POST.get('linea')

        qs = self.consulta(ano, mes)

        if not linea == "0":
            qs = qs.filter(vendedor__linea=linea)

        max_year=qs.aggregate(Max('year'))['year__max']
        total_fact = qs.filter(year=max_year).aggregate(Sum('venta_neto'))["venta_neto__sum"]

        pareto = []
        sum = 0
        for cli in qs.values('id_terc_fa').annotate(fac=Sum('venta_neto')).filter(year=max_year).order_by('-fac').all():
            sum += (int(cli['fac']) / total_fact) * 100
            if sum <= 80:
                pareto.append(cli['id_terc_fa'])

        qs = qs.annotate(tipo=Case(
            When(id_terc_fa__in=pareto,
                 then=Value('Pareto')),
            default=Value('Otros'),
            output_field=CharField(),
        )).order_by('-v_neto')

        lista = list(qs)
        for i in lista:
            i["v_bruta"] = int(i["v_bruta"])
            i["Costo"] = int(i["Costo"])
            i["v_neto"] = int(i["v_neto"])
            i["renta"] = int(i["renta"])
            i["Descuentos"] = int(i["Descuentos"])
        context["lista"] = lista
        return self.render_json_response(context)

    def consulta(self, ano, mes):
        qs = MovimientoVentaBiable.objects.all().values('cliente', 'year').annotate(
            v_bruta=Sum('venta_bruta'),
            v_neto=Sum('venta_neto'),
            Descuentos=Sum('dscto_netos'),
            Costo=Sum('costo_total'),
            renta=Sum('rentabilidad'),
            Margen=(Sum('rentabilidad') / Sum('venta_neto') * 100),
        ).filter(
            year__in=list(map(lambda x: int(x), ano)),
            month__in=list(map(lambda x: int(x), mes))
        )
        return qs


class VentasMes(JSONResponseMixin, AjaxResponseMixin, TemplateView):
    template_name = 'indicadores/ventasxmes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ano_fin = MovimientoVentaBiable.objects.all().aggregate(Max('year'))['year__max']
        ano_ini = MovimientoVentaBiable.objects.all().aggregate(Min('year'))['year__min']
        ano_fin = ano_fin + 1

        context['anos_list'] = list(range(ano_ini, ano_fin))
        return context

    def post_ajax(self, request, *args, **kwargs):
        ultima_actualizacion = Actualizacion.objects.filter(tipo='MOVIMIENTO_VENTAS').latest('fecha').fecha_formateada()
        context = {"fecha_actualizacion": ultima_actualizacion}
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
        context["lista"] = lista
        return self.render_json_response(context)

    def consulta(self, ano):
        qs = MovimientoVentaBiable.objects.values('month').annotate(
            v_bruta=Sum('venta_bruta'),
            v_neto=Sum('venta_neto'),
            Descuentos=Sum('dscto_netos'),
            Costo=Sum('costo_total'),
            renta=Sum('rentabilidad'),
            Margen=(Sum('rentabilidad') / Sum('venta_neto') * 100)
        ).filter(year=ano).order_by('month')
        return qs


class VentasLineaAno(JSONResponseMixin, AjaxResponseMixin, TemplateView):
    template_name = 'indicadores/ventasxlineaxano.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ano_fin = MovimientoVentaBiable.objects.all().aggregate(Max('year'))['year__max']
        ano_ini = MovimientoVentaBiable.objects.all().aggregate(Min('year'))['year__min']
        ano_fin = ano_fin + 1

        context['anos_list'] = list(range(ano_ini, ano_fin))

        return context

    def post_ajax(self, request, *args, **kwargs):
        ultima_actualizacion = Actualizacion.objects.filter(tipo='MOVIMIENTO_VENTAS').latest('fecha').fecha_formateada()
        context = {"fecha_actualizacion": ultima_actualizacion}
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
        context["lista"] = lista
        return self.render_json_response(context)

    def consulta(self, ano, mes):
        qs = MovimientoVentaBiable.objects.all().values('year').annotate(
            v_bruta=Sum('venta_bruta'),
            v_neto=Sum('venta_neto'),
            Descuentos=Sum('dscto_netos'),
            Costo=Sum('costo_total'),
            renta=Sum('rentabilidad'),
            Margen=(Sum('rentabilidad') / Sum('venta_neto') * 100),
        ).filter(
            year__in=list(map(lambda x: int(x), ano)),
            month__in=list(map(lambda x: int(x), mes))
        ).order_by('-v_bruta')
        print(qs.all().count())
        print(qs)
        return qs


class VentasVendedorMes(JSONResponseMixin, AjaxResponseMixin, TemplateView):
    template_name = 'indicadores/ventasxvendedorxmes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ano_fin = MovimientoVentaBiable.objects.all().aggregate(Max('year'))['year__max']
        ano_ini = MovimientoVentaBiable.objects.all().aggregate(Min('year'))['year__min']
        ano_fin = ano_fin + 1

        context['anos_list'] = list(range(ano_ini, ano_fin))

        return context

    def post_ajax(self, request, *args, **kwargs):
        ultima_actualizacion = Actualizacion.objects.filter(tipo='MOVIMIENTO_VENTAS').latest('fecha').fecha_formateada()
        context = {"fecha_actualizacion": ultima_actualizacion}
        ano = self.request.POST.getlist('ano')
        linea = self.request.POST.get('linea')

        qs = self.consulta(ano)

        if not linea == "0":
            qs = qs.filter(vendedor__linea=linea)

        lista = list(qs)
        for i in lista:
            i["v_bruta"] = int(i["v_bruta"])
            i["Costo"] = int(i["Costo"])
            i["v_neto"] = int(i["v_neto"])
            i["renta"] = int(i["renta"])
            i["Descuentos"] = int(i["Descuentos"])
        context["lista"] = lista
        return self.render_json_response(context)

    def consulta(self, ano):
        qs = MovimientoVentaBiable.objects.all().values('month').annotate(
            vendedor_nombre=F('vendedor__nombre'),
            v_bruta=Sum('venta_bruta'),
            v_neto=Sum('venta_neto'),
            Descuentos=Sum('dscto_netos'),
            Costo=Sum('costo_total'),
            renta=Sum('rentabilidad'),
            Margen=(Sum('rentabilidad') / Sum('venta_neto') * 100),
        ).filter(
            year__in=list(map(lambda x: int(x), ano))
        ).order_by('month')
        return qs


class VentasLineaAnoMes(JSONResponseMixin, AjaxResponseMixin, TemplateView):
    template_name = 'indicadores/ventasxlineaxanoxmes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ano_fin = MovimientoVentaBiable.objects.all().aggregate(Max('year'))['year__max']
        ano_ini = MovimientoVentaBiable.objects.all().aggregate(Min('year'))['year__min']
        ano_fin = ano_fin + 1

        context['anos_list'] = list(range(ano_ini, ano_fin))

        return context

    def post_ajax(self, request, *args, **kwargs):
        ultima_actualizacion = Actualizacion.objects.filter(tipo='MOVIMIENTO_VENTAS').latest('fecha').fecha_formateada()
        context = {"fecha_actualizacion": ultima_actualizacion}
        ano = self.request.POST.getlist('anos[]')
        linea = self.request.POST.get('linea')

        qs = self.consulta(ano)

        if not linea == "0":
            qs = qs.filter(vendedor__linea=linea)

        lista = list(qs)
        for i in lista:
            i["v_bruta"] = int(i["v_bruta"])
            i["Costo"] = int(i["Costo"])
            i["v_neto"] = int(i["v_neto"])
            i["renta"] = int(i["renta"])
            i["Descuentos"] = int(i["Descuentos"])
        context["lista"] = lista
        return self.render_json_response(context)

    def consulta(self, ano):
        qs = MovimientoVentaBiable.objects.all().values('year', 'month').annotate(
            v_bruta=Sum('venta_bruta'),
            v_neto=Sum('venta_neto'),
            Descuentos=Sum('dscto_netos'),
            Costo=Sum('costo_total'),
            renta=Sum('rentabilidad'),
            Margen=(Sum('rentabilidad') / Sum('venta_neto') * 100),
        ).filter(
            year__in=list(map(lambda x: int(x), ano))
        ).order_by('month')
        return qs


class VentasClienteMes(JSONResponseMixin, AjaxResponseMixin, TemplateView):
    template_name = 'indicadores/ventasxclientexmes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ano_fin = MovimientoVentaBiable.objects.all().aggregate(Max('year'))['year__max']
        ano_ini = MovimientoVentaBiable.objects.all().aggregate(Min('year'))['year__min']
        ano_fin = ano_fin + 1

        context['anos_list'] = list(range(ano_ini, ano_fin))

        return context

    def post_ajax(self, request, *args, **kwargs):
        ultima_actualizacion = Actualizacion.objects.filter(tipo='MOVIMIENTO_VENTAS').latest('fecha').fecha_formateada()
        context = {"fecha_actualizacion": ultima_actualizacion}
        ano = self.request.POST.getlist('ano')
        linea = self.request.POST.get('linea')

        qs = self.consulta(ano)

        if not linea == "0":
            qs = qs.filter(vendedor__linea=linea)

        total_fact = qs.aggregate(Sum('venta_neto'))["venta_neto__sum"]

        pareto = []
        sum = 0
        for cli in qs.values('id_terc_fa').annotate(fac=Sum('venta_neto')).order_by('-fac').all():
            sum += (int(cli['fac']) / total_fact) * 100
            if sum <= 80:
                pareto.append(cli['id_terc_fa'])

        qs = qs.annotate(tipo=Case(
            When(id_terc_fa__in=pareto,
                 then=Value('Pareto')),
            default=Value('Otros'),
            output_field=CharField(),
        )).order_by('month','cliente')

        lista = list(qs)
        for i in lista:
            i["v_bruta"] = int(i["v_bruta"])
            i["Costo"] = int(i["Costo"])
            i["v_neto"] = int(i["v_neto"])
            i["renta"] = int(i["renta"])
            i["Descuentos"] = int(i["Descuentos"])
        context["lista"] = lista
        return self.render_json_response(context)

    def consulta(self, ano):
        qs = MovimientoVentaBiable.objects.all().values('month', 'id_terc_fa').annotate(
            cliente=F('cliente'),
            v_bruta=Sum('venta_bruta'),
            v_neto=Sum('venta_neto'),
            Descuentos=Sum('dscto_netos'),
            Costo=Sum('costo_total'),
            renta=Sum('rentabilidad'),
            Margen=(Sum('rentabilidad') / Sum('venta_neto') * 100),
        ).filter(
            year__in=list(map(lambda x: int(x), ano))
        )
        return qs
