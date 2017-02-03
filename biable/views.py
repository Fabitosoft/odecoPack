from braces.views import PrefetchRelatedMixin, SelectRelatedMixin
from django.shortcuts import render
from django.views.generic.detail import DetailView

from .models import FacturasBiable, Cliente


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
    prefetch_related = ['mis_movimientos_venta__item_biable']


class ClienteDetailView(DetailView):
    model = Cliente
    template_name = 'biable/cliente_detail.html'
