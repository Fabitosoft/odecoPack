from decimal import Decimal
from django.utils import timezone

from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.template import Context
from django.template.loader import get_template, render_to_string
from django.views import View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import ListView
from django.views.generic import DetailView
from django.conf import settings

from .models import ItemCotizacion, Cotizacion
from productos.models import Producto
from .forms import BusquedaCotiForm


# Create your views here.

class CotizacionDetailView(DetailView):
    model = Cotizacion
    template_name = "cotizaciones/cotizacion_detail.html"

    def get_object(self, queryset=None):
        obj = self.model.objects \
            .select_related('usuario', 'usuario__user_extendido', 'usuario__user_extendido__colaborador') \
            .prefetch_related('items__item', 'items__forma_pago') \
            .get(id=self.kwargs["pk"])

        if obj.estado == "INI":
            obj.razon_social = self.request.GET.get('razon_social')
            obj.nombres_contacto = self.request.GET.get('nombres_contacto')
            obj.apellidos_contacto = self.request.GET.get('apellidos_contacto')
            obj.email = self.request.GET.get('email')
            obj.nro_contacto = self.request.GET.get('nro_contacto')
            obj.ciudad = self.request.GET.get('ciudad')
            obj.pais = self.request.GET.get('pais')
            obj.nro_cotizacion = "%s - %s" % ('CB', obj.id)
            obj.fecha_envio = timezone.now()
            obj.estado = "ENV"
            obj.save()

            subject, from_email, to = "%s - %s" % (
                'Cotizacion', obj.nro_cotizacion), settings.EMAIL_HOST_USER, self.request.GET.get('email')

            ctx = {
                'object': obj,
            }

            text_content = render_to_string('cotizaciones/emails/cotizacion.html', ctx)
            html_content = get_template('cotizaciones/emails/cotizacion.html').render(Context(ctx))
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

        return obj


class CotizacionesListView(ListView):
    model = Cotizacion

    def get_queryset(self):
        query = self.request.GET.get("buscado")
        if not query:
            query = ""
        print(query)
        qs = Cotizacion.objects.filter(
            (Q(usuario=self.request.user) &
             ~Q(estado="INI")) &
            (
                Q(nombres_contacto__icontains=query) |
                Q(nro_cotizacion__icontains=query) |
                Q(ciudad__icontains=query) |
                Q(razon_social__icontains=query) |
                Q(items__item__descripcion_estandar__icontains=query) |
                Q(items__item__referencia__icontains=query)
            )
        ).order_by('-total').distinct()
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_busqueda"] = BusquedaCotiForm(self.request.GET or None)
        return context


class AddItemCantidad(SingleObjectMixin, View):
    model = ItemCotizacion

    def get(self, request, *args, **kwargs):
        delete = False
        item_id = request.GET.get("item")
        item = ItemCotizacion.objects.get(id=item_id)
        qty = Decimal(request.GET.get("qty"))

        if qty < 0.999:
            delete = True
            item.delete()
        else:
            item.cantidad = qty
            item.total = item.precio * qty
            item.save()

        data = {
            "deleted": delete,
            "total_line": item.total,
            "total_cotizacion": item.cotizacion.total
        }
        return JsonResponse(data)


class AddItem(SingleObjectMixin, View):
    model = ItemCotizacion

    def get(self, request, *args, **kwargs):
        coti_id = kwargs["cot_id"]
        item_id = kwargs["item_id"]
        precio = kwargs["precio"]
        forma_pago_id = kwargs["forma_pago"]
        tipo = kwargs["tipo"]

        item = ItemCotizacion.objects.filter(
            Q(item_id=item_id) &
            Q(cotizacion_id=coti_id)
        ).first()

        if not item:
            item = ItemCotizacion()
            if tipo == 1:
                producto = Producto.objects.get(id=item_id)
                item.cantidad = producto.cantidad_empaque
            else:
                item.cantidad = 1

        item.cotizacion_id = coti_id
        if int(tipo) == 1:
            item.item_id = item_id
        else:
            item.banda_id = item_id
        item.precio = precio
        item.forma_pago_id = forma_pago_id
        item.total = int(precio) * item.cantidad
        item.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
