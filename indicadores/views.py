from django.shortcuts import render
from django.views.generic import TemplateView

from biable.models import MovimientoVentaBiable

# Create your views here.
class Prueba(TemplateView):
    template_name = 'indicadores/prueba.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prueba'] = MovimientoVentaBiable.objects.all()
        return context