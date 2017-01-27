from django.conf.urls import url

from .views import (
    TrabajoDiarioDetailView,
    TrabajoDiaView,
    TareaCotizacionDetailView,
    TareaCarteraDetailView,
    TareaEnvioTccDetailView
)

urlpatterns = [
    url(r'trabajo_detail/(?P<pk>[0-9]+)/$', TrabajoDiarioDetailView.as_view(), name='trabajo-detail'),
    url(r'tarea_cotizacion_detalle/(?P<pk>[0-9]+)/$', TareaCotizacionDetailView.as_view(),
        name='tarea-cotizacion-detalle'),
    url(r'tarea_cotizacion_detalle/(?P<pk>[0-9]+)/$', TareaCotizacionDetailView.as_view(), name='tarea-enviotcc-detalle'),
    url(r'tarea_tcc_detalle/(?P<pk>[0-9]+)/$', TareaEnvioTccDetailView.as_view(), name='tarea-enviotcc-detalle'),
    url(r'tarea_cartera_detalle/(?P<pk>[0-9]+)/$', TareaCarteraDetailView.as_view(), name='tarea-cartera-detalle'),
]
