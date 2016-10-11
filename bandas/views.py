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

    def get_queryset(self):
        qs = super().get_queryset()
        return super().get_queryset()

        # def get_queryset(self):
        #     query = self.request.GET.get("buscado")
        #     if not query:
        #         query = ""
        #     print(query)
        #     qs = Banda.objects.filter(
        #         (Q(usuario=self.request.user) &
        #         ~Q(estado="INI")) &
        #         (
        #             Q(nombres_contacto__icontains=query) |
        #             Q(nro_cotizacion__icontains=query) |
        #             Q(ciudad__icontains=query) |
        #             Q(razon_social__icontains=query) |
        #             Q(items__item__descripcion_estandar__icontains=query) |
        #             Q(items__item__referencia__icontains=query)
        #         )
        #     ).order_by('-total').distinct()
        #     return qs
        #
        # def get_context_data(self, **kwargs):
        #     context = super().get_context_data(**kwargs)
        #     context["form_busqueda"] = BusquedaCotiForm(self.request.GET or None)
        #     return context
