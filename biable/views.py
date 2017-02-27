import json

from braces.views import PermissionRequiredMixin
from braces.views import (
    JSONResponseMixin,
    PrefetchRelatedMixin,
    SelectRelatedMixin,
    LoginRequiredMixin,
    AjaxResponseMixin
)
from dal import autocomplete
from django.db.models import F
from django.db.models import Func
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q, Case, Value, When, Sum, CharField
from django.db.models.functions import Concat, Extract, Upper
from django.views.generic import UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from cotizaciones.models import ItemCotizacion
from .models import FacturasBiable, Cliente, MovimientoVentaBiable
from .forms import ContactoEmpresaBuscador, ClienteDetailEditForm, ClienteProductoBusquedaForm


# Create your views here.

class FacturaDetailView(SelectRelatedMixin, PrefetchRelatedMixin, DetailView):
    template_name = 'biable/factura_detail.html'
    model = FacturasBiable
    select_related = [
        'cliente',
        'vendedor',
        'ciudad_biable__ciudad_intranet',
        'ciudad_biable__ciudad_intranet__departamento'
    ]
    prefetch_related = [
        'mis_movimientos_venta__item_biable',
    ]


class ClienteDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    SelectRelatedMixin,
    PrefetchRelatedMixin,
    JSONResponseMixin,
    AjaxResponseMixin,
    UpdateView):
    permission_required = "biable.ver_clientes"
    form_class = ClienteDetailEditForm
    select_related = ['canal', 'industria']
    model = Cliente
    template_name = 'biable/clientes/cliente_detail.html'
    prefetch_related = [
        'mis_compras__vendedor',
        'mis_cotizaciones__usuario',
        'mis_cotizaciones__ciudad_despacho',
        'mis_cotizaciones__ciudad_despacho__departamento',
        'mis_cotizaciones__ciudad_despacho__departamento__pais',
        'mis_cotizaciones__mis_remisiones',
        'mis_cotizaciones__mis_remisiones__factura_biable',
        'grupo__mis_empresas',
        'mis_despachos__ciudad',
        'mis_despachos__ciudad__departamento',
        'mis_compras__ciudad_biable__ciudad_intranet',
        'mis_compras__ciudad_biable__ciudad_intranet__departamento'
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.object.mis_contactos.filter(sucursal__isnull=True).all()
        context['contactos_sin_sucursal'] = qs
        si_sucursales = self.object.mis_sucursales.filter(
            vendedor_real__colaborador__usuario__user=self.request.user).exists()
        context['es_vendedor_cliente'] = si_sucursales
        context['tab'] = "custom"
        context['form_busqueda_historico_precios'] = ClienteProductoBusquedaForm(self.request.GET or None)
        query = self.request.GET.get('buscar')
        if query:
            context['tab'] = "BHP"
            qsP = MovimientoVentaBiable.objects.select_related(
                'factura',
                'item_biable',
                'factura__sucursal',
                'factura__vendedor',
                'factura__cliente'
            ).all().filter(
                Q(factura__cliente=self.object) &
                (
                    Q(item_biable__id_referencia__icontains=query) |
                    Q(item_biable__descripcion__icontains=query) |
                    Q(item_biable__id_item__icontains=query)
                )
            ).order_by('-factura__fecha_documento').distinct()[:10]
            context['historico_precios_producto_ventas'] = qsP

            qsC = ItemCotizacion.objects.all().select_related(
                'cotizacion',
                'item',
                'banda',
                'articulo_catalogo'
            ).filter(
                Q(cotizacion__cliente_biable=self.object) &
                (
                    Q(item__descripcion_estandar__icontains=query) |
                    Q(item__descripcion_comercial__icontains=query) |
                    Q(item__referencia__icontains=query) |
                    Q(banda__descripcion_estandar__icontains=query) |
                    Q(banda__descripcion_comercial__icontains=query) |
                    Q(banda__referencia__icontains=query) |
                    Q(articulo_catalogo__referencia__icontains=query) |
                    Q(articulo_catalogo__nombre__icontains=query) |
                    Q(p_n_lista_descripcion__icontains=query) |
                    Q(p_n_lista_referencia__icontains=query)
                )
            ).order_by('-cotizacion__fecha_envio').distinct()[:10]
            context['historico_precios_producto_cotizaciones'] = qsC

        return context

    def post_ajax(self, request, *args, **kwargs):
        nit = request.POST.get('nit')
        cliente = Cliente.objects.get(nit=nit)
        context = {}
        fecha_hoy = timezone.now().date()
        year_ini = fecha_hoy.year - 3
        qs = MovimientoVentaBiable.objects.values(
            'item_biable__descripcion',
            'item_biable__categoria_mercadeo',
            'item_biable__categoria_mercadeo_dos',
            'item_biable__id_referencia'
        ).annotate(
            year=Extract('factura__fecha_documento', 'year'),
            month=Extract('factura__fecha_documento', 'month'),
            day=Extract('factura__fecha_documento', 'day'),
            vendedor=Upper(Case(
                When(factura__vendedor__colaborador__isnull=True, then=F('factura__vendedor__nombre')),
                default=Concat('factura__vendedor__colaborador__usuario__user__first_name', Value(' '),
                               'factura__vendedor__colaborador__usuario__user__last_name'),
                output_field=CharField(),
            )),
            venta_neta=Sum('venta_neto'),
            cantidad_neta=Sum('cantidad'),
            factura_venta=Concat('factura__tipo_documento', Value('-'), 'factura__nro_documento'),
            nombre_producto=Concat('item_biable__descripcion', Value(' ('), 'item_biable__id_item', Value(')'),
                                   output_field=CharField()),
            linea=F('factura__vendedor__linea_ventas__nombre')
        ).filter(
            factura__cliente=cliente,
            factura__fecha_documento__year__gte=year_ini
        ).order_by('factura__fecha_documento')
        lista = list(qs)
        for i in lista:
            i["venta_neta"] = int(i["venta_neta"])
            i["cantidad_neta"] = int(i["cantidad_neta"])
        context['ventasxproductos'] = lista
        return self.render_json_response(context)


class ClienteAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Cliente.objects.none()

        qs = Cliente.objects.all()

        if self.q:
            qs = qs.filter(
                Q(nombre__icontains=self.q) |
                Q(nit__istartswith=self.q)
            )

        return qs


class ClienteBiableListView(PermissionRequiredMixin, LoginRequiredMixin, SelectRelatedMixin, ListView):
    model = Cliente
    template_name = 'biable/clientes/cliente_list.html'
    context_object_name = 'clientes'
    paginate_by = 15
    select_related = ['canal', 'grupo', 'industria']
    permission_required = "biable.ver_clientes"
    tipo = "todos"

    def get_queryset(self):
        q = self.request.GET.get('busqueda')
        qs = super().get_queryset()
        if self.tipo == "por_vendedor":
            qs = qs.filter(
                mis_sucursales__vendedor_real__colaborador__usuario__user=self.request.user
            ).order_by('nombre').distinct()

        if q:
            qs = qs.exclude(nit='').order_by('nombre').distinct()
            qs = qs.filter(
                Q(nombre__icontains=q) |
                Q(grupo__nombre__icontains=q) |
                Q(nit__icontains=q)
            )
        else:
            if self.tipo == "todos":
                qs = qs.none()
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_busqueda'] = ContactoEmpresaBuscador(self.request.GET or None)
        return context


class ClienteBiablePorVendedorView(ClienteBiableListView):
    tipo = "por_vendedor"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_busqueda'].helper.form_action = reverse('biable:clientes-lista-mis-clientes')
        return context
