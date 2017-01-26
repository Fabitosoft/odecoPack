from django.conf.urls import url

from .views import (
    TareaDiaListView,
    TareaDiaUpdateView,
    TrabajoDiarioDetailView,
    TrabajoDiaView,
    TareaCotizacionDetailView,
    TareaCarteraDetailView,
    TareaEnvioTccDetailView
)

urlpatterns = [
    url(r'^list/$', TareaDiaListView.as_view(), name='lista_tareas'),
    url(r'^hoy/$', TrabajoDiaView.as_view(), name='tareas_hoy'),
    url(r'tarea_update/(?P<pk>[0-9]+)/$', TareaDiaUpdateView.as_view(), name='tarea-update'),
    url(r'tarea_detail/(?P<pk>[0-9]+)/$', TrabajoDiarioDetailView.as_view(), name='tarea-detail'),
    url(r'tarea_cotizacion_detalle/(?P<pk>[0-9]+)/$', TareaCotizacionDetailView.as_view(),
        name='tarea-cotizacion-detalle'),
    url(r'tarea_cotizacion_detalle/(?P<pk>[0-9]+)/$', TareaCotizacionDetailView.as_view(), name='tarea-enviotcc-detalle'),
    url(r'tarea_tcc_detalle/(?P<pk>[0-9]+)/$', TareaEnvioTccDetailView.as_view(), name='tarea-enviotcc-detalle'),
    url(r'tarea_cartera_detalle/(?P<pk>[0-9]+)/$', TareaCarteraDetailView.as_view(), name='tarea-cartera-detalle'),
]
