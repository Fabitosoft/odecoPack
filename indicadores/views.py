from django.shortcuts import render
from django.views.generic.list import ListView

from biable.models import DataBiable


# Create your views here.
class Prueba(ListView):
    model = DataBiable

    def get_queryset(self):
        return super().get_queryset()
