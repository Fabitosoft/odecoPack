import json
from braces.views import SelectRelatedMixin
from django.db.models import Case, CharField, Sum, Max, Min, Count, When, F, Q, Value, IntegerField
from django.db.models.functions import Concat, Extract
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, ListView
from django.contrib.auth.models import User

from braces.views import JSONResponseMixin, AjaxResponseMixin, LoginRequiredMixin

from biable.models import (
    MovimientoVentaBiable,
    Actualizacion,
    LineaVendedorBiable,
    Cartera
)

from usuarios.models import Colaborador
from cotizaciones.models import Cotizacion


# from crm.models import VtigerCrmentity, VtigerAccountscf

# Create your views here.

class InformeVentasConLineaMixin(object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lineas_list'] = LineaVendedorBiable.objects.all()
        return context


class InformeVentasConAnoMixin(object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ano_fin = MovimientoVentaBiable.objects.all().aggregate(Max('year'))['year__max']
        ano_ini = MovimientoVentaBiable.objects.all().aggregate(Min('year'))['year__min']

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


class VentasVendedor(LoginRequiredMixin, SelectRelatedMixin, JSONResponseMixin, AjaxResponseMixin,
                     InformeVentasConAnoMixin,
                     FechaActualizacionMovimientoVentasMixin, TemplateView):
    template_name = 'indicadores/venta/ventasxvendedor.html'
    select_related = [u"vendedor"]

    # def get_context_data(self, **kwargs):
    #     # accounts_list = VtigerCrmentity.objects.using('biable').values('crmid').filter(smownerid__user_name='alalopros',
    #     #                                                                                setype='Accounts')
    #     # nits = VtigerAccountscf.objects.using('biable').values('cf_751').filter(accountid__in=accounts_list)
    #     # nits = list(nits)
    #     # nits_filtro = []
    #     # for nit in nits:
    #     #     nits_filtro.append(nit['cf_751'])
    #     # resultado = MovimientoVentaBiable.objects.filter(id_terc_fa__in=nits_filtro)
    #     # print(resultado)
    #     # print(nits)
    #     # list(accounts_list)
    #     return context

    def post_ajax(self, request, *args, **kwargs):
        context = {}
        ultima_actualizacion = self.get_ultima_actualizacion()
        if ultima_actualizacion:
            context["fecha_actualizacion"] = ultima_actualizacion

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
        current_user = self.request.user
        qsFinal = None
        qs = MovimientoVentaBiable.objects.all().values('vendedor__nombre').annotate(
            # vendedor_nombre=F('vendedor__nombre'),
            vendedor_nombre=Case(
                When(vendedor__activo=False, then=Value('VENDEDORES INACTIVOS')),
                default=F('vendedor__nombre'),
                output_field=CharField(),
            ),
            v_bruta=Sum('venta_bruta'),
            v_neto=Sum('venta_neto'),
            Descuentos=Sum('dscto_netos'),
            Costo=Sum('costo_total'),
            renta=Sum('rentabilidad'),
            Margen=(Sum('rentabilidad') / Sum('venta_neto') * 100),
            linea=F('vendedor__linea_ventas__nombre'),
        )

        if not current_user.has_perm('biable.reporte_ventas_todos_vendedores'):
            usuario = get_object_or_404(Colaborador, usuario__user=current_user)
            qsFinal = qs.filter(
                (
                    Q(year__in=list(map(lambda x: int(x), ano))) &
                    Q(month__in=list(map(lambda x: int(x), mes)))
                ) &
                (
                    Q(vendedor__colaborador__in=usuario.subalternos.all()) |
                    Q(vendedor__colaborador=usuario)
                )
            ).distinct()
        else:
            qsFinal = qs.filter(
                Q(year__in=list(map(lambda x: int(x), ano))) &
                Q(month__in=list(map(lambda x: int(x), mes)))).order_by('-vendedor__activo', 'day')
        return qsFinal.order_by('-vendedor__activo')


class VentasVendedorConsola(LoginRequiredMixin, SelectRelatedMixin, JSONResponseMixin, AjaxResponseMixin,
                            InformeVentasConAnoMixin,
                            FechaActualizacionMovimientoVentasMixin,
                            TemplateView):
    template_name = 'indicadores/venta/consolaxventasxvendedor.html'
    select_related = [u"vendedor"]

    def post_ajax(self, request, *args, **kwargs):
        context = {}
        ultima_actualizacion = self.get_ultima_actualizacion()
        if ultima_actualizacion:
            context["fecha_actualizacion"] = ultima_actualizacion

        ano = self.request.POST.getlist('anos[]')
        mes = self.request.POST.getlist('meses[]')
        qs = self.consulta(ano, mes)
        lista = list(qs)

        for i in lista:
            i["v_neto"] = int(i["v_neto"])
        context["lista"] = lista
        return self.render_json_response(context)

    def consulta(self, ano, mes):
        current_user = self.request.user
        qsFinal = None
        qs = MovimientoVentaBiable.objects.all().values('day').annotate(
            vendedor_nombre=Case(
                When(vendedor__activo=False, then=Value('VENDEDORES INACTIVOS')),
                default=F('vendedor__nombre'),
                output_field=CharField(),
            ),
            cliente=F('cliente'),
            documento=Concat('tipo_documento', Value('-'), 'nro_documento'),
            tipo_documento=F('tipo_documento'),
            v_neto=Sum('venta_neto'),
            linea=F('vendedor__linea_ventas__nombre'),
        )
        if not current_user.has_perm('biable.reporte_ventas_todos_vendedores'):
            usuario = get_object_or_404(Colaborador, usuario__user=current_user)
            qsFinal = qs.filter(
                Q(year__in=list(map(lambda x: int(x), ano))) &
                Q(month__in=list(map(lambda x: int(x), mes))) &
                (
                    Q(vendedor__colaborador__in=usuario.subalternos.all())
                    | Q(vendedor__colaborador=usuario)
                    | Q(vendedor__activo=False)
                )
            ).distinct().order_by('-vendedor__activo', 'day')
        else:
            qsFinal = qs.filter(
                Q(year__in=list(map(lambda x: int(x), ano))) &
                Q(month__in=list(map(lambda x: int(x), mes)))).order_by('-vendedor__activo', 'day')
        return qsFinal


class VentasClientes(LoginRequiredMixin, JSONResponseMixin, AjaxResponseMixin, InformeVentasConAnoMixin,
                     InformeVentasConLineaMixin,
                     FechaActualizacionMovimientoVentasMixin, TemplateView):
    template_name = 'indicadores/venta/ventasxcliente.html'

    def post_ajax(self, request, *args, **kwargs):
        context = {}
        ultima_actualizacion = self.get_ultima_actualizacion()
        if ultima_actualizacion:
            context["fecha_actualizacion"] = ultima_actualizacion

        ano = self.request.POST.getlist('anos[]')
        mes = self.request.POST.getlist('meses[]')
        linea = self.request.POST.get('linea')

        qs = self.consulta(ano, mes)

        if not linea == "0":
            qs = qs.filter(vendedor__linea_ventas_id=linea)

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


class VentasClientesAno(LoginRequiredMixin, JSONResponseMixin, AjaxResponseMixin, InformeVentasConAnoMixin,
                        InformeVentasConLineaMixin,
                        FechaActualizacionMovimientoVentasMixin, TemplateView):
    template_name = 'indicadores/venta/ventasxclientexano.html'

    def post_ajax(self, request, *args, **kwargs):
        context = {}
        ultima_actualizacion = self.get_ultima_actualizacion()
        if ultima_actualizacion:
            context["fecha_actualizacion"] = ultima_actualizacion
        ano = self.request.POST.getlist('anos[]')
        mes = self.request.POST.getlist('meses[]')
        linea = self.request.POST.get('linea')

        qs = self.consulta(ano, mes)

        if not linea == "0":
            qs = qs.filter(vendedor__linea_ventas_id=linea)

        max_year = qs.aggregate(Max('year'))['year__max']
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


class VentasMes(LoginRequiredMixin, JSONResponseMixin, AjaxResponseMixin, InformeVentasConLineaMixin,
                InformeVentasConAnoMixin,
                FechaActualizacionMovimientoVentasMixin, TemplateView):
    template_name = 'indicadores/venta/ventasxmes.html'

    def post_ajax(self, request, *args, **kwargs):
        context = {}
        ultima_actualizacion = self.get_ultima_actualizacion()
        if ultima_actualizacion:
            context["fecha_actualizacion"] = ultima_actualizacion

        ano = self.request.POST.get('ano')
        linea = self.request.POST.get('linea')
        qs = self.consulta(ano)

        if not linea == "0":
            qs = qs.filter(vendedor__linea_ventas_id=linea)

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


class VentasLineaAno(LoginRequiredMixin, JSONResponseMixin, AjaxResponseMixin, InformeVentasConAnoMixin,
                     InformeVentasConLineaMixin,
                     FechaActualizacionMovimientoVentasMixin, TemplateView):
    template_name = 'indicadores/venta/ventasxlineaxano.html'

    def post_ajax(self, request, *args, **kwargs):
        context = {}
        ultima_actualizacion = self.get_ultima_actualizacion()
        if ultima_actualizacion:
            context["fecha_actualizacion"] = ultima_actualizacion

        ano = self.request.POST.getlist('anos[]')
        mes = self.request.POST.getlist('meses[]')
        linea = self.request.POST.get('linea')

        qs = self.consulta(ano, mes)

        if not linea == "0":
            qs = qs.filter(vendedor__linea_ventas_id=linea)

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
        return qs


class VentasVendedorMes(SelectRelatedMixin, JSONResponseMixin, AjaxResponseMixin, InformeVentasConAnoMixin,
                        FechaActualizacionMovimientoVentasMixin, InformeVentasConLineaMixin, TemplateView):
    template_name = 'indicadores/venta/ventasxvendedorxmes.html'
    select_related = [u"vendedor"]

    def post_ajax(self, request, *args, **kwargs):
        context = {}
        ultima_actualizacion = self.get_ultima_actualizacion()
        if ultima_actualizacion:
            context["fecha_actualizacion"] = ultima_actualizacion

        ano = self.request.POST.getlist('ano')
        linea = self.request.POST.get('linea')

        qs = self.consulta(ano)

        if not linea == "0":
            qs = qs.filter(vendedor__linea_ventas_id=linea)

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
            vendedor_nombre=Case(
                When(vendedor__activo=False, then=Value('VENDEDORES INACTIVOS')),
                default=F('vendedor__nombre'),
                output_field=CharField(),
            ),
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


class VentasLineaAnoMes(JSONResponseMixin, AjaxResponseMixin, InformeVentasConAnoMixin, InformeVentasConLineaMixin,
                        FechaActualizacionMovimientoVentasMixin, TemplateView):
    template_name = 'indicadores/venta/ventasxlineaxanoxmes.html'

    def post_ajax(self, request, *args, **kwargs):
        context = {}
        ultima_actualizacion = self.get_ultima_actualizacion()
        if ultima_actualizacion:
            context["fecha_actualizacion"] = ultima_actualizacion

        ano = self.request.POST.getlist('anos[]')
        linea = self.request.POST.get('linea')

        qs = self.consulta(ano)

        if not linea == "0":
            qs = qs.filter(vendedor__linea_ventas_id=linea)

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


class VentasClienteMes(JSONResponseMixin, AjaxResponseMixin, InformeVentasConAnoMixin, InformeVentasConLineaMixin,
                       FechaActualizacionMovimientoVentasMixin, TemplateView):
    template_name = 'indicadores/venta/ventasxclientexmes.html'

    def post_ajax(self, request, *args, **kwargs):
        context = {}
        ultima_actualizacion = self.get_ultima_actualizacion()
        if ultima_actualizacion:
            context["fecha_actualizacion"] = ultima_actualizacion

        ano = self.request.POST.getlist('ano')
        linea = self.request.POST.get('linea')

        qs = self.consulta(ano)

        if not linea == "0":
            qs = qs.filter(vendedor__linea_ventas_id=linea)

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
        )).order_by('month', 'cliente')

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


class CarteraVencimientos(JSONResponseMixin, ListView):
    template_name = 'indicadores/cartera/vencimientos.html'
    model = Cartera
    context_object_name = 'cartera_list'

    def get_context_data(self, **kwargs):
        current_user = self.request.user
        context = super().get_context_data(**kwargs)
        ultima_actualizacion = Actualizacion.tipos.cartera_vencimiento()
        if ultima_actualizacion:
            ultima_actualizacion = ultima_actualizacion.latest('fecha')
            context = {"fecha_actualizacion": ultima_actualizacion.fecha_formateada()}

        qsFinal = None

        qs = self.get_queryset()
        qs = qs.values(
            'nro_documento',
            'tipo_documento',
            'forma_pago',
            'dias_vencido',
            'dias_para_vencido',
            'fecha_ultimo_pago',
            'fecha_documento',
            'fecha_vencimiento',
            'debe',
            'recaudado',
            'a_recaudar',
            'cliente',
            'client_id',
        ).annotate(
            tipo=Case(
                When(esta_vencido=True,
                     then=Value('Vencido')),
                default=Value('Corriente'),
                output_field=CharField(),
            ),
            vendedor_nombre=Case(
                When(vendedor__activo=False, then=Value('VENDEDORES INACTIVOS')),
                default=F('vendedor__nombre'),
                output_field=CharField(),
            ),
            forma_pago_tipo=Case(
                When(forma_pago__lte=30, then=Value('0-30')),
                When(forma_pago__lte=60, then=Value('31-60')),
                When(forma_pago__lte=90, then=Value('61-90')),
                default=Value('Más de 90'),
                output_field=CharField(),
            ),
        ).order_by('-dias_vencido', '-debe')

        if not current_user.has_perm('biable.ver_carteras_todos'):
            usuario = get_object_or_404(Colaborador, usuario__user=current_user)
            clientes = Cartera.objects.values_list('client_id').filter(vendedor__colaborador=usuario,
                                                                       esta_vencido=True).distinct()
            clientes_subalternos = Cartera.objects.values_list('client_id').filter(
                vendedor__colaborador__in=usuario.subalternos.all()).distinct()
            qsFinal = qs.filter(
                (
                    Q(vendedor__colaborador__in=usuario.subalternos.all())
                    | Q(vendedor__colaborador=usuario)
                    | Q(vendedor__activo=False)
                    | Q(client_id__in=clientes, esta_vencido=True)
                    | Q(client_id__in=clientes_subalternos)
                )
            ).distinct()
        else:
            qsFinal = qs

        lista = list(qsFinal)

        for i in lista:
            i["debe"] = int(i["debe"])
            i["recaudado"] = int(i["recaudado"])
            i["a_recaudar"] = int(i["a_recaudar"])

        context['datos'] = json.dumps(lista,
                                      cls=self.json_encoder_class,
                                      **self.get_json_dumps_kwargs()).encode('utf-8')
        return context


class TrabajoCotizacionVentaVendedorAnoMes(LoginRequiredMixin, JSONResponseMixin, AjaxResponseMixin,
                                           InformeVentasConAnoMixin,
                                           FechaActualizacionMovimientoVentasMixin, TemplateView):
    template_name = 'indicadores/trabajo/cotizacionesyventasxanoxmes.html'

    def post_ajax(self, request, *args, **kwargs):
        context = {}
        ultima_actualizacion = self.get_ultima_actualizacion()
        if ultima_actualizacion:
            context["fecha_actualizacion"] = ultima_actualizacion

        ano = self.request.POST.getlist('anos[]')
        mes = self.request.POST.getlist('meses[]')

        qs = self.consulta(ano, mes)
        lista = qs
        for i in lista:
            i["nro_cotizaciones"] = int(i["nro_cotizaciones"])
            i["total_cotizaciones"] = int(i["total_cotizaciones"])
            i["descuentos_cotizaciones"] = int(i["descuentos_cotizaciones"])
            i["facturacion"] = int(i["facturacion"])
        context["lista"] = lista
        return self.render_json_response(context)

    def consulta(self, ano, mes):
        current_user = self.request.user
        qsFinal = None
        print(ano)
        print(mes)

        qsCotizacion = Cotizacion.objects.values('usuario').annotate(
            vendedor=Concat('usuario__first_name', Value(' '), 'usuario__last_name'),
            ano_consulta=Extract('fecha_envio', 'year'),
            mes_consulta=Extract('fecha_envio', 'month'),
            dia_consulta=Extract('fecha_envio', 'day'),
            dia_semana_consulta=Extract('fecha_envio', 'week_day'),
            hora_consulta=Extract('fecha_envio', 'hour'),
            nro_cotizaciones=Count('id'),
            total_cotizaciones=Sum('total'),
            descuentos_cotizaciones=Sum('descuento'),
            facturacion=Value(0,output_field=IntegerField()),
            vendedor__colaborador__usuario=Value(0,output_field=IntegerField()),

        ).filter(fecha_envio__month__in=mes, fecha_envio__year__in=ano).order_by('fecha_envio', 'dia_semana_consulta')

        qsFacturacion = MovimientoVentaBiable.objects.values('vendedor__colaborador__usuario').annotate(
            usuario=Value(0,output_field=IntegerField()),
            vendedor=Concat('vendedor__colaborador__usuario__user__first_name', Value(' '),
                            'vendedor__colaborador__usuario__user__last_name'),
            ano_consulta=F('year'),
            mes_consulta=F('month'),
            dia_consulta=F('day'),
            dia_semana_consulta=Value(0,output_field=IntegerField()),
            hora_consulta=Value(0,output_field=IntegerField()),
            nro_cotizaciones=Value(0,output_field=IntegerField()),
            total_cotizaciones=Value(0,output_field=IntegerField()),
            descuentos_cotizaciones=Value(0,output_field=IntegerField()),
            facturacion=Sum('venta_neto'),
        ).filter(day__in=mes, year__in=ano)

        uno = list(qsCotizacion)
        dos = list(qsFacturacion)
        tres = []
        tres.extend(uno)
        tres.extend(dos)
        return tres
