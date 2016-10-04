from django.shortcuts import render
from django.views.generic.base import View

from usuarios.mixins import LoginRequiredMixin
# Create your views here.

class HomeView(LoginRequiredMixin,View):
    template_name = "cotizaciones/emails/cotizacion.html"
    def get(self, request, *args, **kwargs):

        return render(request, self.template_name)