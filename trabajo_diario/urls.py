from django.conf.urls import url

from .views import (
    TareaDiaListView,
    TareaDiaUpdateView
)

urlpatterns = [
    url(r'^list/$', TareaDiaListView.as_view(), name='lista_tareas'),
    url(r'tarea_update/(?P<pk>[0-9]+)/$', TareaDiaUpdateView.as_view(), name='tarea-update'),
]
