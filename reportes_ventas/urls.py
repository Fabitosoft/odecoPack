from django.conf.urls import url

from .views import (
    VentasVendedor,
    VentasMes,
    VentasLineaAno,
    VentasClientes,
    VentasClientesAno,
    VentasClienteMes,
    VentasLineaAnoMes,
    VentasVendedorMes,
    VentasVendedorConsola,
    CarteraVencimientos,
    TrabajoCotizacionVentaVendedorAnoMes,
    VentasProductoAnoMes,
    MargenesFacturaView,
    MargenesItemView
)

urlpatterns = [
    url(r'^ventxvend/', VentasVendedor.as_view(), name='ventasxvendedor'),
    url(r'^ventxclie/', VentasClientes.as_view(), name='ventasxcliente'),
    url(r'^ventxcliexano/', VentasClientesAno.as_view(), name='ventasxclientexano'),
    url(r'^ventxcliexmes/', VentasClienteMes.as_view(), name='ventasxclientexmes'),
    url(r'^ventxmes/', VentasMes.as_view(), name='ventasxmes'),
    url(r'^ventxlineaxano/', VentasLineaAno.as_view(), name='ventasxlineaxano'),
    url(r'^ventxlineaxanoxmes/', VentasLineaAnoMes.as_view(), name='ventasxlineaxanoxmes'),
    url(r'^ventxvendxmes/', VentasVendedorMes.as_view(), name='ventasxvendedorxmes'),
    url(r'^ventxproduxmesxano/', VentasProductoAnoMes.as_view(), name='ventasxproductoxanoxmes'),
    url(r'^consola_ventas/', VentasVendedorConsola.as_view(), name='consolaventas'),
    url(r'^cartera_vencimientos/', CarteraVencimientos.as_view(), name='cartera_vencimientos'),
    url(r'^margen_factura/', MargenesFacturaView.as_view(), name='margen_factura'),
    url(r'^margen_item/', MargenesItemView.as_view(), name='margen_item'),
    url(r'^cotizacion_venta_vendedorxanoxmes/', TrabajoCotizacionVentaVendedorAnoMes.as_view(),
        name='cotizacion_venta_vendedorxanoxmes'),
]
