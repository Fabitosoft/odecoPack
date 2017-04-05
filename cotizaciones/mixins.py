from io import BytesIO

from django.db.models import Q
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template, render_to_string
from django.template import Context
from django.conf import settings
from weasyprint import HTML

from bandas.models import Banda
from configuraciones.models import DominiosEmail, EmailConfiguration
from seguimientos.models import SeguimientoComercialCliente
from .models import FormaPago
from productos.models import (
    Producto,
    ArticuloCatalogo
)

from .forms import ItemCotizacionOtrosForm
from listasprecios.forms import ProductoBusqueda
from .models import Cotizacion

from biable.models import Colaborador, SucursalBiable


class EnviarCotizacionMixin(object):
    def enviar_cotizacion(self, cotizacion, user):
        version_cotizacion = cotizacion.version

        from_ventas_email = EmailConfiguration.objects.first().email_ventas_from
        if not from_ventas_email:
            from_ventas_email = settings.DEFAULT_FROM_EMAIL

        enviar_como = user.user_extendido.email_envio_como
        if enviar_como:
            enviar_como = '%s - %s' % (user.user_extendido.email_envio_como, user.get_full_name())
        else:
            enviar_como = 'ODECOPACK - %s' % (user.get_full_name())

        if user.email:
            email_split = user.email.split('@')
            if email_split[-1] in list(DominiosEmail.objects.values_list('dominio', flat=True).all()):
                from_email = "%s <%s>" % (enviar_como, user.email)
            else:
                from_email = "%s <%s>" % (enviar_como, from_ventas_email)
        else:
            from_email = "%s <%s>" % (enviar_como, from_ventas_email)
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

        if not cotizacion.cliente_nuevo:
            colaboradores = SucursalBiable.objects.values('vendedor_real__colaborador_id').filter(
                cliente_id=cotizacion.cliente_biable_id, vendedor_real__isnull=False
            ).distinct()
            if colaboradores.exists():
                if colaboradores.count() == 1:
                    colaborador = Colaborador.objects.get(pk=colaboradores.first()['vendedor_real__colaborador_id'])
                    cotizacion.usuario = colaborador.usuario.user

                    cotizacion.save()
            else:
                colaborador = Colaborador.objects.get(usuario__user=user)

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
                                     reply_to=[user.email])
        msg.attach_alternative(html_content, "text/html")

        msg.attach(nombre_archivo_cotizacion, output.getvalue(), 'application/pdf')

        if cotizacion.mis_imagenes:
            for imagen in cotizacion.mis_imagenes.all():
                try:
                    docfile = imagen.imagen.read()
                    if docfile:
                        nombre_archivo = imagen.imagen.name.split("/")[-1]
                        msg.attach(nombre_archivo, docfile)
                        docfile.close()
                    else:
                        pass
                except:
                    pass

        msg.send()
        output.close()
        cotizacion.save()

        if not cotizacion.cliente_nuevo:
            seguimiento = SeguimientoComercialCliente()
            seguimiento.cotizacion = cotizacion
            seguimiento.creado_por = self.request.user
            seguimiento.cliente = cotizacion.cliente_biable

            observacion_adicional = "<p> Valor Cotización: " + str(cotizacion.total) + "</p>"
            if cotizacion.descuento:
                observacion_adicional += "<p> Descuento Cotización: " + str(cotizacion.descuento) + "</p>"

            seguimiento.observacion_adicional = observacion_adicional
            if version_cotizacion > 1:
                seguimiento.tipo_accion = "Envío version " + str(version_cotizacion)
            else:
                seguimiento.tipo_accion = "Nueva"
            seguimiento.save()


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


class CotizacionesCambioCantidadesAjaxMixin(object):
    def cambiar_cantidad(self, item, cantidad=None, cantidad_perdida=None, motivo_cantidad_perdida=None):
        if cantidad_perdida is not None:
            item.motivo_venta_perdida = motivo_cantidad_perdida
            if cantidad_perdida <= 0 or motivo_cantidad_perdida == 'NA':
                item.cantidad_venta_perdida = 0
                item.motivo_venta_perdida = 'NA'
            elif cantidad_perdida > item.cantidad:
                item.cantidad_venta_perdida = item.cantidad
            else:
                item.cantidad_venta_perdida = cantidad_perdida

        if cantidad:
            item.cantidad = cantidad
            if cantidad < item.cantidad_venta_perdida:
                item.cantidad_venta_perdida = 0
                item.motivo_venta_perdida = 'NA'

        item.cantidad_total = item.cantidad - item.cantidad_venta_perdida
        descuento = (item.precio * item.cantidad_total) * (item.porcentaje_descuento / 100)
        item.descuento = descuento

        item.valor_venta_perdida_total = item.cantidad_venta_perdida * item.precio

        item.total = (item.precio * item.cantidad_total) - descuento
        item.save()


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

            qs_articulos_catalogo = ArticuloCatalogo.activos.todos().filter(
                Q(referencia__icontains=query) |
                Q(nombre__icontains=query) |
                Q(categoria__icontains=query)
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
