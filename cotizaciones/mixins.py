from io import BytesIO

from django.db.models import Q
from django.utils import timezone
from django.core.mail import get_connection
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect
from django.template.loader import get_template, render_to_string
from django.template import Context
from django.conf import settings
from django.contrib import messages
from weasyprint import HTML

from bandas.models import Banda
from .models import FormaPago
from productos.models import (
    Producto,
    ArticuloCatalogo
)

from .forms import CotizacionCrearForm, CotizacionEnviarForm, ItemCotizacionOtrosForm
from listasprecios.forms import ProductoBusqueda
from .models import Cotizacion

from biable.models import Colaborador


class EnviarCotizacionMixin(object):
    def enviar_cotizacion(self, cotizacion, user):
        connection = get_connection(host=settings.EMAIL_HOST_ODECO,
                                    port=settings.EMAIL_PORT_ODECO,
                                    username=settings.EMAIL_HOST_USER_ODECO,
                                    password=settings.EMAIL_HOST_PASSWORD_ODECO,
                                    use_tls=settings.EMAIL_USE_TLS_ODECO
                                    )

        version_cotizacion = cotizacion.version
        from_email = "ODECOPACK / COMPONENTES <%s>" % (settings.EMAIL_HOST_USER_ODECO)
        to = cotizacion.email
        subject = "%s - %s" % ('Cotizacion', cotizacion.nro_cotizacion)
        if version_cotizacion > 1:
            subject = "%s, version %s" % (subject, cotizacion.version)

        ctx = {
            'object': cotizacion,
        }

        try:
            colaborador = Colaborador.objects.get(usuario__user=user)
        except Colaborador.DoesNotExist:
            colaborador = None

        if colaborador:
            if colaborador.foto_perfil:
                url_avatar = colaborador.foto_perfil.url
                ctx['avatar'] = url_avatar

        nombre_archivo_cotizacion = "Cotizacion Odecopack - CB %s.pdf" % (cotizacion.id)
        if version_cotizacion > 1:
            ctx['version'] = cotizacion.version
            nombre_archivo_cotizacion = "Cotizacion Odecopack - CB %s ver %s.pdf" % (
                cotizacion.id, cotizacion.version)

        text_content = render_to_string('cotizaciones/emails/cotizacion.html', ctx)

        html_content = get_template('cotizaciones/emails/cotizacion.html').render(Context(ctx))

        output = BytesIO()
        HTML(string=html_content).write_pdf(target=output)
        msg = EmailMultiAlternatives(subject, text_content, from_email, to=[to], bcc=[user.email],
                                     connection=connection, reply_to=[user.email])
        msg.attach_alternative(html_content, "text/html")

        msg.attach(nombre_archivo_cotizacion, output.getvalue(), 'application/pdf')
        msg.send()
        output.close()
        cotizacion.save()


class CotizacionesActualesMixin(object):
    def get_context_data(self, **kwargs):
        usuario = self.request.user
        context = super().get_context_data(**kwargs)
        context["cotizaciones_activas"] = Cotizacion.objects.filter(
            Q(usuario=usuario) &
            (
                Q(estado="INI") |
                Q(en_edicion=True)
            )
        ).order_by('id')
        return context


class ListaPreciosMixin(object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['busqueda_producto_form'] = ProductoBusqueda(self.request.GET or None)
        if self.object:
            context["forma_item_otro"] = ItemCotizacionOtrosForm(initial={'cotizacion_id': self.object.id})
        self.get_lista_precios(context)
        return context

    def get_lista_precios(self, context):
        query = self.request.GET.get("buscar")
        if query:
            context['tab'] = "LP"
            qs_bandas = Banda.activos.componentes().filter(
                Q(referencia__icontains=query) |
                Q(descripcion_estandar__icontains=query) |
                Q(descripcion_comercial__icontains=query)
            ).distinct()

            qs_componentes = Producto.activos.componentes().select_related("unidad_medida").filter(
                Q(referencia__icontains=query) |
                Q(descripcion_estandar__icontains=query) |
                Q(descripcion_comercial__icontains=query)
            ).distinct().order_by('-modified')

            qs_articulos_catalogo = ArticuloCatalogo.objects.filter(
                Q(activo=True) &
                (
                    Q(referencia__icontains=query) |
                    Q(nombre__icontains=query) |
                    Q(categoria__icontains=query)
                )
            ).distinct()

            context['object_list_componentes'] = qs_componentes
            context['object_list_articulos_catalogo'] = qs_articulos_catalogo
            context['object_list_bandas'] = qs_bandas
            context["forma_de_pago"] = self.request.GET.get('tipo')
            self.get_forma_porcentaje_pago(context)

    def get_forma_porcentaje_pago(self, context):
        if self.request.GET.get("tipo"):
            context['formas_pago_porcentaje'] = FormaPago.objects.filter(
                id=self.request.GET.get("tipo")).first().porcentaje
        else:
            if FormaPago.objects.all():
                context['formas_pago_porcentaje'] = FormaPago.objects.first().porcentaje
            else:
                context['formas_pago_porcentaje'] = 0
