from django.db.models import Q
from django.views.generic import ListView
from django.utils import timezone
from django.db.models import Max

from .models import FormaPago
from cotizaciones.models import Cotizacion
from productos.models import Producto
from .forms import ProductoBusqueda
from cotizaciones.forms import CotizacionForm
from usuarios.mixins import LoginRequiredMixin
from bandas.models import Banda


# Create your views here.
class ListaPreciosView(LoginRequiredMixin, ListView):
    """
    Display an individual :model:`myapp.MyModel`.

    **Context**

    ``mymodel``
        An instance of :model:`myapp.MyModel`.

    **Template:**

    :template:`myapp/my_template.html`
    """
    model = Producto
    template_name = "listasprecios/listaprecio_list.html"

    def get_queryset(self):
        query = self.request.GET.get("buscar")
        if not query:
            query = "Ningun atributo de busqueda"

        qs = self.model.activos.componentes().select_related("unidad_medida").filter(
            Q(referencia__icontains=query) |
            Q(descripcion_estandar__icontains=query)
        ).distinct().order_by('-modified')
        return qs

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['formu'] = ProductoBusqueda(self.request.GET or None)

        query = self.request.GET.get("buscar")
        if not query:
            query = "Ningun atributo de busqueda"
        context['object_list_bandas'] = Banda.activos.componentes().filter(
            Q(referencia__icontains=query) |
            Q(descripcion_estandar__icontains=query)
        ).distinct()

        # segun el tipo, obtiene el porcentaje que se aplicará a la lista de precios
        if self.request.GET.get("tipo"):
            context['formas_pago_porcentaje'] = FormaPago.objects.filter(
                id=self.request.GET.get("tipo")).first().porcentaje
        else:
            if FormaPago.objects.all():
                context['formas_pago_porcentaje'] = FormaPago.objects.first().porcentaje
            else:
                context['formas_pago_porcentaje'] = 0

        cotizacion = Cotizacion.objects.filter(
            Q(usuario=self.request.user) &
            Q(estado__exact="INI")
        ).last()

        if self.request.GET.get('crear') and not cotizacion:
            cotizacion = Cotizacion()
            cotizacion.usuario = self.request.user
            cotizacion.razon_social = self.request.GET.get('razon_social')
            cotizacion.nombres_contacto = self.request.GET.get('nombres_contacto')
            cotizacion.apellidos_contacto = self.request.GET.get('apellidos_contacto')
            cotizacion.email = self.request.GET.get('email')
            cotizacion.nro_contacto = self.request.GET.get('nro_contacto')
            cotizacion.ciudad = self.request.GET.get('ciudad')
            cotizacion.pais = self.request.GET.get('pais')
            cotizacion.fecha_envio = timezone.now()
            cotizacion.estado = "INI"
            cotizacion.save()
            cotizacion.nro_cotizacion = "%s - %s" % ('CB', cotizacion.id)
            cotizacion.save()

        if self.request.GET.get('descartar') and cotizacion:
            cotizacion.delete()
            cotizacion = None

        if cotizacion:
            context["cotizacion_form"] = CotizacionForm(instance=cotizacion)
            context["cotizacion_form"].id = cotizacion.id
            context["cotizacion_id"] = cotizacion.id
            context["cotizacion_total"] = cotizacion.total
            context["items_cotizacion"] = cotizacion.items.all()
        else:
            context["cotizacion_form"] = CotizacionForm()

        context["forma_de_pago"] = self.request.GET.get('tipo')

        return context
