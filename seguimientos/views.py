from django.contrib.auth.models import User
from django.shortcuts import render
from django.views.generic.list import ListView

from .models import SeguimientoComercialCliente


# Create your views here.
class UsuariosConSeguimientoGestionComercialListView(ListView):
    model = User
    context_object_name = 'lista_usuarios'
    template_name = 'seguimientos/gestion_comercial/usuarios_gestion_comercial_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        qs2 = SeguimientoComercialCliente.objects.values_list('creado_por').filter(
            creado_por__isnull=False).all().distinct()
        qs = qs.filter(id__in=qs2)[0:100]
        return qs


class GestionComercialUsuarioList(ListView):
    model = SeguimientoComercialCliente
    template_name = 'seguimientos/gestion_comercial/usuarios_gestion_comercial_usuario.html'
    context_object_name = 'mi_gestion_comercial'

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related(
            'cliente',
            'creado_por',
            'cotizacion',
            'cotizacion__cliente_biable',
            'comentario_cotizacion',
            'seguimiento_cliente',
            'seguimiento_cartera__tarea',
            'seguimiento_cartera__tarea__factura',
            'seguimiento_envio_tcc',
            'seguimiento_envio_tcc__tarea',
            'seguimiento_envio_tcc__tarea__envio',
            'seguimiento_cotizacion',
            'seguimiento_cotizacion__tarea',
            'seguimiento_cotizacion__tarea__cotizacion',
            'contacto',
        ).filter(creado_por__pk=self.kwargs.get('pk'))
        return qs
