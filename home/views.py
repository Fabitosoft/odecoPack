from django.shortcuts import render
from django.views.generic.base import TemplateView

from usuarios.mixins import LoginRequiredMixin


# Create your views here.

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "index.html"
