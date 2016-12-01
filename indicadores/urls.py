from django.conf.urls import url

from .views import (
    VentasVendedor,
    FacturacionAno,
    FacturacionAnoLinea,
    VentasClientes,
    VentasClientesAno
)

urlpatterns = [
    url(r'^ventxvend/', VentasVendedor.as_view(), name='ventasxvendedor'),
    url(r'^ventxclie/', VentasClientes.as_view(), name='ventasxcliente'),
    url(r'^ventxcliexano/', VentasClientesAno.as_view(), name='ventasxclientexano'),
    url(r'^factxano/', FacturacionAno.as_view(), name='facturacionxano'),
    url(r'^factxanoxlinea/', FacturacionAnoLinea.as_view(), name='facturacionxanoxlinea'),
]
