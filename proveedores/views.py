from django.db.models import Case, When, DecimalField
from django.db.models import Q
from django.shortcuts import render
from django.views.generic import ListView
from django.db.models import Max, Count

from .models import ListaPrecio, VariableListaPrecio
# Create your views here.

class ListaPreciosView(ListView):
    model = ListaPrecio

    def get_queryset(self):

        USD_VS_COP = VariableListaPrecio.objects.filter(referencia="USD_VS_COP").first().value
        EUR_VS_USD = VariableListaPrecio.objects.filter(referencia="EUR_VS_USD").first().value
        FACT_IMPO = VariableListaPrecio.objects.filter(referencia="FACT_IMPO").first().value
        MRG = (VariableListaPrecio.objects.filter(referencia="MRG").first().value/100)


        print(USD_VS_COP*EUR_VS_USD*FACT_IMPO)
        print(EUR_VS_USD*2)
        print(FACT_IMPO*2)

        qs =self.model.objects.values(
            'producto__referencia',
            'producto__descripcion_estandar',
            'producto__cantidad_empaque',
            'producto__fabricante',
            'producto__unidad_medida',
            'proveedor__moneda__nombre'
        ).annotate(
            costo_base=Max('valor'),
            costo_dolar=Max(Case(
                When(proveedor__moneda__nombre='USD', then='valor'),
                default=0,
                output_field=DecimalField(max_digits=10, decimal_places=3),
            )),
            costo_euro=Max(Case(
                When(proveedor__moneda__nombre='EUR', then='valor'),
                default=0,
                output_field=DecimalField(max_digits=10, decimal_places=3),
            )),
            costo_odeco=Case(
                When(proveedor__moneda__nombre='EUR', then=Max('valor')*EUR_VS_USD*USD_VS_COP*FACT_IMPO),
                When(proveedor__moneda__nombre='USD', then=Max('valor') * USD_VS_COP * FACT_IMPO),
                When(proveedor__moneda__nombre='COP', then=Max('valor')),
                default=0,
                output_field=DecimalField(max_digits=10, decimal_places=3),
            ),
            precio_contado_base=Case(
                When(proveedor__moneda__nombre='EUR', then=(Max('valor')*EUR_VS_USD*USD_VS_COP*FACT_IMPO)/(1-MRG)),
                When(proveedor__moneda__nombre='USD', then=(Max('valor') * USD_VS_COP * FACT_IMPO)/(1-MRG)),
                When(proveedor__moneda__nombre='COP', then=Max('valor')/(1-MRG)),
                default=0,
                output_field=DecimalField(max_digits=10, decimal_places=3),
            )
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
        print(qs)
        return qs

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        print("Entro")
        context['CF_30'] = (VariableListaPrecio.objects.filter(referencia="CF_30").first().value / 100)
        context['CF_60'] = (VariableListaPrecio.objects.filter(referencia="CF_60").first().value / 100)
        context['OEM_CONT'] = (VariableListaPrecio.objects.filter(referencia="OEM_CONT").first().value / 100)
        context['OEM_30'] = (VariableListaPrecio.objects.filter(referencia="OEM_30").first().value / 100)
        context['OEM_60'] = (VariableListaPrecio.objects.filter(referencia="OEM_60").first().value / 100)
        context['DIST_CONT'] = (VariableListaPrecio.objects.filter(referencia="DIST_CONT").first().value / 100)
        context['DIST_30'] = (VariableListaPrecio.objects.filter(referencia="DIST_30").first().value / 100)
        context['DIST_60'] = (VariableListaPrecio.objects.filter(referencia="DIST_60").first().value / 100)

        return context

