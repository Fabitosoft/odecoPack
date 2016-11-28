from django.conf.urls import url

from .views import VentasVendedor, FacturacionAno, FacturacionAnoLinea

urlpatterns = [
    url(r'^ventxvend/', VentasVendedor.as_view(), name='ventasxvendedor'),
    url(r'^factxano/', FacturacionAno.as_view(), name='facturacionxano'),
    url(r'^factxanoxlinea/', FacturacionAnoLinea.as_view(), name='facturacionxanoxlinea'),
]
