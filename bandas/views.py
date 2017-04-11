from django.shortcuts import render

# Create your views here.
from django.views.generic import DetailView
from django.views.generic import ListView

from .models import Banda


class BandaDetailView(DetailView):
    model = Banda

    def get_queryset(self):
        qs = self.model.objects.select_related(
            'serie',
            'tipo',
            'material',
            'color',
            'material_varilla',
            'empujador_tipo',
        ).all()
        return qs


class BandaListView(ListView):
    model = Banda
    context_object_name = 'bandas_list'

    def get_queryset(self):
        return super().get_queryset()