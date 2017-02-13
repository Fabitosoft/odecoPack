from braces.views import PrefetchRelatedMixin, SelectRelatedMixin, LoginRequiredMixin
from dal import autocomplete
from django.db.models import Q, Count
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .models import FacturasBiable, Cliente
from .forms import ContactoEmpresaBuscador


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
        'mis_movimientos_venta__item_biable'
    ]


class ClienteDetailView(PrefetchRelatedMixin, DetailView):
    model = Cliente
    template_name = 'biable/cliente_detail.html'
    prefetch_related = [
        'mis_compras__vendedor',
        'mis_cotizaciones__usuario',
        'mis_cotizaciones__mis_remisiones',
        'mis_cotizaciones__mis_remisiones__factura_biable',
        'grupo__mis_empresas',
        'mis_despachos__ciudad',
        'mis_despachos__ciudad__departamento',
    ]


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


class ClienteBiableListView(LoginRequiredMixin, SelectRelatedMixin, ListView):
    model = Cliente
    template_name = 'biable/cliente_list.html'
    context_object_name = 'clientes'
    paginate_by = 15
    select_related = ['canal', 'grupo', 'industria']

    def get_queryset(self):
        q = self.request.GET.get('busqueda')
        qs = super().get_queryset()

        if q:
            qs = qs.exclude(nit='').order_by('nombre').distinct()
            qs = qs.filter(
                Q(nombre__icontains=q) |
                Q(grupo__nombre__icontains=q) |
                Q(nit__icontains=q)
            )
        else:
            qs = qs.none()

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_busqueda'] = ContactoEmpresaBuscador(self.request.GET or None)
        return context
