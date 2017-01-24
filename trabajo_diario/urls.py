from django.conf.urls import url

from .views import (
    TareaDiaListView,
    TareaDiaUpdateView,
    TrabajoDiarioDetailView
)

urlpatterns = [
    url(r'^list/$', TareaDiaListView.as_view(), name='lista_tareas'),
    url(r'tarea_update/(?P<pk>[0-9]+)/$', TareaDiaUpdateView.as_view(), name='tarea-update'),
    url(r'tarea_detail/(?P<pk>[0-9]+)/$', TrabajoDiarioDetailView.as_view(), name='tarea-detail'),
]
