from django.conf.urls import url

from .views import (
    ContactosEmpresaCreateView,
    ContactosEmpresaUpdateView,
    AgendaContactoListView
)

urlpatterns = [
    url(r'^add/(?P<nit>[\w-]+)$', ContactosEmpresaCreateView.as_view(), name='crear_contacto_empresa'),
    url(r'^actualizar/(?P<pk>[0-9]+)$', ContactosEmpresaUpdateView.as_view(), name='actualizar_contacto_empresa'),
    url(r'^agenda_contactos/$', AgendaContactoListView.as_view(), name='agenda-contactos'),
]
