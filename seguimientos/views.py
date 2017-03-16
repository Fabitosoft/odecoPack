from django.contrib.auth.models import User
from django.views.generic.list import ListView

from .mixins import SeguimientoGestionComercialMixin
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


class GestionComercialUsuarioList(SeguimientoGestionComercialMixin, ListView):
    model = SeguimientoComercialCliente
    template_name = 'seguimientos/gestion_comercial/usuarios_gestion_comercial_usuario.html'
    context_object_name = 'mi_gestion_comercial'

    def get_queryset(self):
        tipo = self.request.GET.get('tipo_seguimiento_comercial')
        qs = self.get_seguimiento_comercial(nro_registros=100, usuario_pk=self.kwargs.get('pk'), tipo=tipo)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vendedor'] = User.objects.get(pk=self.kwargs.get('pk'))
        return context
