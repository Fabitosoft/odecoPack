from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.template import Context
from django.template.loader import get_template, render_to_string
from django.urls import reverse
from django.views.generic import ListView
from django.db.models import Max

from django.conf import settings

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

        #segun el tipo, obtiene el porcentaje que se aplicará a la lista de precios
        if self.request.GET.get("tipo"):
            context['formas_pago_porcentaje'] = FormaPago.objects.filter(
                id=self.request.GET.get("tipo")).first().porcentaje_lp.value
        else:
            context['formas_pago_porcentaje'] = FormaPago.objects.first().porcentaje_lp.value

        cotizacion = Cotizacion.objects.filter(usuario=self.request.user).last()
        if not cotizacion or cotizacion.estado == 'ENV':
            cotizacion = Cotizacion()
            cotizacion.usuario=self.request.user
            cotizacion.save()
        context["cotizacion_form"] = CotizacionForm(self.request.GET or None, instance=cotizacion)
        context["cotizacion_form"].id = cotizacion.id

        context["cotizacion_id"] = cotizacion.id
        context["cotizacion_total"] = cotizacion.total
        context["items_cotizacion"] = cotizacion.items.all()
        context["forma_de_pago"] = self.request.GET.get('tipo')

        return context

    def get(self, request, *args, **kwargs):
        # subject, from_email, to = 'prueba', settings.EMAIL_HOST_USER, 'fabio.garcia.sanchez@gmail.com'
        #
        # ctx={
        #     'uno': 'valor uno',
        #     'dos': 'valor dos'
        # }
        # text_content = render_to_string('listasprecios/emails/cotizacion.html', ctx)
        # html_content = get_template('listasprecios/emails/cotizacion.html').render(Context(ctx))
        # msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        # msg.attach_alternative(html_content, "text/html")
        # msg.send()
        if self.request.user.user_extendido.es_colaborador():
            return super().get(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)
        #return HttpResponseRedirect(reverse('home:home-index'))


