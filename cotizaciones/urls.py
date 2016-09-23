from django.conf.urls import url

from .views import AddItem, AddItemCantidad

urlpatterns = [
    url(r'^add/(?P<item_id>[0-9]+)/(?P<precio>[0-9]+)$', AddItem.as_view(), name='add_item_cotizacion'),
    url(r'^add_qty/$', AddItemCantidad.as_view(), name='add_qty_item_cotizacion'),
]
