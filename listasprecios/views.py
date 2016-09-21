from django.db.models import Q
from django.views.generic import ListView
from django.db.models import Max

from .models import ListaPrecio, FormaPago
# Create your views here.

class ListaPreciosView(ListView):
    model = ListaPrecio

    def get_queryset(self):
        # EUR_VS_USD = VariableListaPrecio.objects.filter(referencia="EUR_VS_USD").first().value
        # FACT_IMPO = VariableListaPrecio.objects.filter(referencia="FACT_IMPO").first().value
        # MRG = (VariableListaPrecio.objects.filter(referencia="MRG").first().value/100)

        print(self.request.GET.get("forma_pago_id"))

        qs =self.model.objects.values(
            'producto__referencia',
            'producto__descripcion_estandar',
            'producto__cantidad_empaque',
            'producto__fabricante',
            'producto__unidad_medida',
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
        query = self.request.GET.get("q")
        if query:
            qs = qs.filter(
                Q(producto__referencia__icontains=query) |
                Q(producto__descripcion_estandar__icontains=query) |
                Q(producto__fabricante__icontains=query)
            ).distinct()
        #qs =self.model.objects.select_related('producto','proveedor').all()
        #Members.objects.values('designation').annotate(dcount=Count('designation'))
        return qs

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        print("Entro")
        # context['CF_30'] = (VariableListaPrecio.objects.filter(referencia="CF_30").first().value / 100)
        # context['CF_60'] = (VariableListaPrecio.objects.filter(referencia="CF_60").first().value / 100)
        # context['OEM_CONT'] = (VariableListaPrecio.objects.filter(referencia="OEM_CONT").first().value / 100)
        # context['OEM_30'] = (VariableListaPrecio.objects.filter(referencia="OEM_30").first().value / 100)
        # context['OEM_60'] = (VariableListaPrecio.objects.filter(referencia="OEM_60").first().value / 100)
        # context['DIST_CONT'] = (VariableListaPrecio.objects.filter(referencia="DIST_CONT").first().value / 100)
        # context['DIST_30'] = (VariableListaPrecio.objects.filter(referencia="DIST_30").first().value / 100)
        context['formas_pago'] = FormaPago.objects.all()
        context['formas_pago_porcentaje'] = FormaPago.objects.filter(id=self.request.GET.get("forma_pago_id")).first().porcentaje_lp.value
        context['formas_pago_id_selected'] = self.request.GET.get("forma_pago_id")
        return context
