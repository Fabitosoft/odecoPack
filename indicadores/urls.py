from django.conf.urls import url

from .views import (
    VentasVendedor,
    VentasMes,
    VentasLineaAno,
    VentasClientes,
    VentasClientesAno
)

urlpatterns = [
    url(r'^ventxvend/', VentasVendedor.as_view(), name='ventasxvendedor'),
    url(r'^ventxclie/', VentasClientes.as_view(), name='ventasxcliente'),
    url(r'^ventxcliexano/', VentasClientesAno.as_view(), name='ventasxclientexano'),
    url(r'^ventxmes/', VentasMes.as_view(), name='ventasxmes'),
    url(r'^ventxlineaxano/', VentasLineaAno.as_view(), name='ventasxlineaxano'),
]
