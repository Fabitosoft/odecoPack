from django.conf.urls import url

from .views import (
    FacturaDetailView,
    ClienteDetailView
)

urlpatterns = [
    url(r'^detalle_factura/(?P<pk>[0-9]+)$', FacturaDetailView.as_view(), name='detalle_factura'),
    url(r'^detalle_cliente/(?P<pk>[0-9]+)$', ClienteDetailView.as_view(), name='detalle_cliente'),
]
