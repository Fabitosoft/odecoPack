from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import DetailView

from .models import ItemCotizacion, Cotizacion


# Create your views here.
class CotizacionDetailView(DetailView):
    model = Cotizacion

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        obj = self.model.objects.filter(id=self.kwargs["pk"]).prefetch_related('items__item').first()
        return obj


class AddItem(SingleObjectMixin, View):
    model = ItemCotizacion

    def get(self, request, *args, **kwargs):
        cotizacion = Cotizacion.objects.filter(usuario=self.request.user).last()
        item_id = kwargs["item_id"]
        precio = kwargs["precio"]
        item = cotizacion.items.filter(item__id=item_id).first()
        if not item:
            item = ItemCotizacion()
            item.cantidad = 1
        item.cotizacion = cotizacion
        item.item_id = item_id
        item.precio = precio
        item.total = int(precio) * item.cantidad
        item.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class AddItemCantidad(SingleObjectMixin, View):
    model = ItemCotizacion

    def get(self, request, *args, **kwargs):
        delete = False
        item_id = request.GET.get("item")
        item = ItemCotizacion.objects.filter(id=item_id).first()
        qty = int(request.GET.get("qty"))

        if qty < 1:
            delete = True
            item.delete()
        else:
            item.cantidad = qty
            item.total = item.precio*qty
            item.save()

        data = {
            "deleted": delete,
            "total_line":item.total,
            "total_cotizacion":item.cotizacion.total
        }
        return JsonResponse(data)

