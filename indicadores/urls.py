from django.conf.urls import url

from .views import VentasVendedor, FacturacionAno

urlpatterns = [
    url(r'^ventxvend/', VentasVendedor.as_view(), name='ventasxvendedor'),
    url(r'^factxano/', FacturacionAno.as_view(), name='facturacionxano'),
]
