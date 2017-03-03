from django.conf.urls import url

from .views import (
    FacturaDetailView,
    ClienteDetailView,
    ClienteAutocomplete,
    ClienteBiableListView,
    ClienteBiablePorVendedorView,
    ClienteSeguimientoCreateView
)

urlpatterns = [
    url(r'^detalle_factura/(?P<pk>[0-9]+)$', FacturaDetailView.as_view(), name='detalle_factura'),
    url(r'^detalle_cliente/(?P<pk>[\w-]+)$', ClienteDetailView.as_view(), name='detalle_cliente'),
    url(r'^cliente-autocomplete/$', ClienteAutocomplete.as_view(), name='cliente-autocomplete'),
    url(r'^clientes-lista/$', ClienteBiableListView.as_view(), name='clientes-lista'),
    url(r'^mis-clientes-lista/$', ClienteBiablePorVendedorView.as_view(), name='clientes-lista-mis-clientes'),
    url(r'^add_seguimiento_cliente/(?P<nit>[\w-]+)$', ClienteSeguimientoCreateView.as_view(), name='crear_seguimiento_cliente'),
]
