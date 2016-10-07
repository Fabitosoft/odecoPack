from django.conf.urls import url

from .views import BandaListView, BandaDetailView

urlpatterns = [
    url(r'^list/$', BandaListView.as_view(), name='listar_bandas'),
    url(r'^detalle/(?P<pk>[0-9]+)$', BandaDetailView.as_view(), name='detalle_banda'),

]
