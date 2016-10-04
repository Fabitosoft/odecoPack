from django.conf.urls import url

from .views import AddItem, AddItemCantidad, EnviarCotitacion

urlpatterns = [
    url(r'^add/(?P<item_id>[0-9]+)/(?P<precio>[0-9]+)/(?P<forma_pago>[0-9]+)/(?P<cot_id>[0-9]+)$', AddItem.as_view(), name='add_item_cotizacion'),
    url(r'^add_qty/$', AddItemCantidad.as_view(), name='add_qty_item_cotizacion'),
    url(r'^detalle/(?P<pk>[0-9]+)$', EnviarCotitacion.as_view(), name='detail_cotizacion'),
]
