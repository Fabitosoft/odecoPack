from django.conf.urls import url

from .views import (
    UsuariosConSeguimientoGestionComercialListView,
    GestionComercialUsuarioList
)

urlpatterns = [
    url(r'^usuarios_gestion_comercial_lista/$', UsuariosConSeguimientoGestionComercialListView.as_view(),
        name='usuarios_gestion_comercial_list'),
    url(r'^gestion_comercial_usuario/(?P<pk>[0-9]+)$', GestionComercialUsuarioList.as_view(),
        name='usuarios_gestion_comercial'),
]
