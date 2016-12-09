from django.conf.urls import url

from .views import (
    VentasVendedor,
    VentasMes,
    VentasLineaAno,
    VentasClientes,
    VentasClientesAno,
    VentasLineaAnoMes,
    VentasVendedorMes,
    VentasVendedorConsola
)

urlpatterns = [
    url(r'^ventxvend/', VentasVendedor.as_view(), name='ventasxvendedor'),
    url(r'^ventxclie/', VentasClientes.as_view(), name='ventasxcliente'),
    url(r'^ventxcliexano/', VentasClientesAno.as_view(), name='ventasxclientexano'),
    url(r'^ventxmes/', VentasMes.as_view(), name='ventasxmes'),
    url(r'^ventxlineaxano/', VentasLineaAno.as_view(), name='ventasxlineaxano'),
    url(r'^ventxlineaxanoxmes/', VentasLineaAnoMes.as_view(), name='ventasxlineaxanoxmes'),
    url(r'^ventxvendxmes/', VentasVendedorMes.as_view(), name='ventasxvendedorxmes'),
    url(r'^consola_ventas/', VentasVendedorConsola.as_view(), name='consolaventas'),
]
