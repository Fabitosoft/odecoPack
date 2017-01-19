from django.conf.urls import url

from .views import (
    FacturaDetailView
)

urlpatterns = [
    url(r'^detalle_factura/(?P<pk>[0-9]+)$', FacturaDetailView.as_view(), name='detalle_factura'),
]
