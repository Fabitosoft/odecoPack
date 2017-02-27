from .models import Moneda


class TaxasCambioMixin(object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        if usuario.has_perm('importaciones.ver_tasas_actuales'):
            context['monedas_lista'] = Moneda.objects.all().order_by("-nombre")
        return context
