from django.db.models import Q
from django.views.generic import ListView
from django.db.models import Max

from .models import ListaPrecio, FormaPago
from cotizaciones.models import Cotizacion
from .forms import ProductoBusqueda
from cotizaciones.forms import CotizacionForm

from usuarios.mixins import LoginRequiredMixin


# Create your views here.

class ListaPreciosView(LoginRequiredMixin,ListView):
    model = ListaPrecio

    def get_queryset(self):
        query = self.request.GET.get("buscar")
        print(query)
        if not query:
            query = "Ningun atributo de busqueda"

        qs = self.model.objects.filter(
            Q(producto__referencia__icontains=query) |
            Q(producto__descripcion_estandar__icontains=query) |
            Q(producto__fabricante__icontains=query)
        ).distinct().values(
            'producto__referencia',
            'producto__descripcion_estandar',
            'producto__cantidad_empaque',
            'producto__fabricante',
            'producto__unidad_medida__nombre',
            'proveedor__moneda__nombre',
            'proveedor__moneda__moneda_cambio__cambio',
            'proveedor__moneda__variablebasica__margen_deseado',
            'proveedor__moneda__variablebasica__factor_importacion',
            'producto_id'
        ).annotate(
            costo_me=Max('valor'),
            factor_cambio=Max('proveedor__moneda__moneda_cambio__cambio'),
            factor_importacion=Max('proveedor__moneda__variablebasica__factor_importacion'),
            margen=Max('proveedor__moneda__variablebasica__margen_deseado'),
            costo_cop=Max('proveedor__moneda__moneda_cambio__cambio') * Max('valor') * Max(
                'proveedor__moneda__variablebasica__factor_importacion'),
            precio_base=(Max('proveedor__moneda__moneda_cambio__cambio') * Max('valor') * Max(
                'proveedor__moneda__variablebasica__factor_importacion') / (
                             1 - Max('proveedor__moneda__variablebasica__margen_deseado')))
        ).order_by('-modified')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formu'] = ProductoBusqueda(self.request.GET or None)
        if self.request.GET.get("tipo"):
            context['formas_pago_porcentaje'] = FormaPago.objects.filter(
                id=self.request.GET.get("tipo")).first().porcentaje_lp.value
        else:
            context['formas_pago_porcentaje'] = FormaPago.objects.first().porcentaje_lp.value

        cotizacion = Cotizacion.objects.filter(usuario=self.request.user).last()
        print(cotizacion)
        if not cotizacion or cotizacion.estado == 'ENV':
            cotizacion = Cotizacion()
            cotizacion.usuario=self.request.user
            cotizacion.save()
        context["cotizacion_form"] = CotizacionForm(self.request.GET or None)
        context["cotizacion_total"] = cotizacion.total
        context["items_cotizacion"] = cotizacion.items.all()
        return context
