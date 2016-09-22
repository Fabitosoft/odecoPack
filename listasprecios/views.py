from django.db.models import Q
from django.views.generic import ListView
from django.db.models import Max

from .models import ListaPrecio, FormaPago
from .forms import ProductoBusqueda
# Create your views here.

class ListaPreciosView(ListView):
    model = ListaPrecio

    def get_queryset(self):
        qs =self.model.objects.values(
            'producto__referencia',
            'producto__descripcion_estandar',
            'producto__cantidad_empaque',
            'producto__fabricante',
            'producto__unidad_medida__nombre',
            'proveedor__moneda__nombre',
            'proveedor__moneda__moneda_cambio__cambio',
            'proveedor__moneda__variablebasica__margen_deseado',
            'proveedor__moneda__variablebasica__factor_importacion'
        ).annotate(
            costo_me=Max('valor'),
            factor_cambio=Max('proveedor__moneda__moneda_cambio__cambio'),
            factor_importacion=Max('proveedor__moneda__variablebasica__factor_importacion'),
            margen=Max('proveedor__moneda__variablebasica__margen_deseado'),
            costo_cop=Max('proveedor__moneda__moneda_cambio__cambio')*Max('valor')*Max('proveedor__moneda__variablebasica__factor_importacion'),
            precio_base=(Max('proveedor__moneda__moneda_cambio__cambio')*Max('valor')*Max('proveedor__moneda__variablebasica__factor_importacion')/(1-Max('proveedor__moneda__variablebasica__margen_deseado')))
        )
        query = self.request.GET.get("buscar")
        if query:
            qs = qs.filter(
                Q(producto__referencia__icontains=query) |
                Q(producto__descripcion_estandar__icontains=query) |
                Q(producto__fabricante__icontains=query)
            ).distinct()
        return qs

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['formu']=ProductoBusqueda(self.request.GET or None)
        if self.request.GET.get("tipo"):
            context['formas_pago_porcentaje'] = FormaPago.objects.filter(id=self.request.GET.get("tipo")).first().porcentaje_lp.value
        else:
            context['formas_pago_porcentaje'] = FormaPago.objects.first().porcentaje_lp.value
        return context
