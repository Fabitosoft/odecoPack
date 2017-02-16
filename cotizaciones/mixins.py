from io import BytesIO

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

from .forms import CotizacionCrearForm, CotizacionEnviarForm
from .models import Cotizacion

from biable.models import Colaborador


class EnviarCotizacionMixin(object):
    tipo = None

    def post(self, request, *args, **kwargs):
        print("inicio mixin")
        id_cotizacion = self.request.POST.get('id')

        if self.tipo == "Enviar" and id_cotizacion:
            cotizacion = Cotizacion.objects.get(id=id_cotizacion)
            formulario = CotizacionEnviarForm(self.request.POST, instance=cotizacion)
            cotizacion = self.procesar_formulario(formulario)
            if cotizacion:
                if cotizacion.estado == "INI":
                    cotizacion.estado = "ENV"
                if not cotizacion.items.exists():
                    mensaje = "No se puede enviar una cotización sin items"
                    messages.add_message(self.request, messages.ERROR, mensaje)
                    return redirect('cotizaciones:cotizador')
                self.enviar(cotizacion)

        if self.tipo == "Reenviar":
            cotizacion = Cotizacion.objects.get(id=id_cotizacion)
            self.enviar(cotizacion)
        print("en post mixin")
        return super().post(request, *args, **kwargs)

    def enviar(self, cotizacion):
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

        user = User.objects.get(username=self.request.user)

        try:
            colaborador = Colaborador.objects.get(usuario__user=user)
        except Colaborador.DoesNotExist:
            colaborador = None

        if colaborador:
            if colaborador.foto_perfil:
                url_avatar = colaborador.foto_perfil.url
                ctx['avatar'] = url_avatar

        nombre_archivo_cotizacion = "Cotizacion Odecopack - CB %s.pdf" % (cotizacion.id)
        if version_cotizacion:
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

    def procesar_formulario(self, formulario):
        cotizacion = None
        if formulario.is_valid():
            print(formulario.ciudad_despacho)
            print("entro es valido")
            cotizacion = formulario.instance
            cotizacion.usuario = self.request.user
            es_cliente_nuevo = cotizacion.cliente_nuevo
            es_otra_ciudad = cotizacion.otra_ciudad
            cotizacion.fecha_envio = timezone.now()

            if not es_otra_ciudad:
                cotizacion.ciudad = None
                cotizacion.pais = None
            else:
                cotizacion.ciudad_despacho = None

            if not es_cliente_nuevo:
                cotizacion.razon_social = None
            else:
                cotizacion.cliente_biable = None

            cotizacion.save()
            cotizacion = Cotizacion.objects.get(id=cotizacion.id)

            if cotizacion.en_edicion:
                cotizacion.en_edicion = False
                cotizacion.version += 1
            cotizacion.nro_cotizacion = "%s - %s" % ('CB', cotizacion.id)
        else:
            print("entro es invalido")
        return cotizacion
