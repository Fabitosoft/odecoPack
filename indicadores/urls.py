from django.conf.urls import url

from .views import VentasVendedor

urlpatterns = [
    url(r'^ventxvend/', VentasVendedor.as_view(), name='ventasxvendedor'),
]
