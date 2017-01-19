from django.shortcuts import render
from django.views.generic.detail import DetailView

from .models import FacturasBiable


# Create your views here.

class FacturaDetailView(DetailView):
    template_name = 'biable/factura_detail.html'
    model = FacturasBiable
