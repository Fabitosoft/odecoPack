from io import BytesIO

from django.core.mail import get_connection
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404
from django.template.loader import get_template
from django.urls import reverse
from django.db.models import Q
from django.template import Context
from django.conf import settings
from django.views import View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import ListView
from django.views.generic import DetailView, FormView
from django.forms import inlineformset_factory
from django.utils import timezone
from django.contrib import messages

import mistune
from weasyprint import HTML

from braces.views import SelectRelatedMixin

from biable.models import Colaborador
from ..models import (
    Cotizacion,
    RemisionCotizacion,
    TareaCotizacion,
    ComentarioCotizacion)

from ..forms import (
    BusquedaCotiForm,
    RemisionCotizacionForm,
    RemisionCotizacionFormHelper,
    TareaCotizacionForm,
    TareaCotizacionFormHelper,
    ComentarioCotizacionForm
)
from ..mixins import EnviarCotizacionMixin


class CotizacionDetailView(SelectRelatedMixin, DetailView):
    model = Cotizacion
    select_related = (
        'usuario',
        'usuario__user_extendido',
        'usuario__user_extendido__colaborador'
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        RemisionFormSet = inlineformset_factory(
            parent_model=Cotizacion,
            model=RemisionCotizacion,
            fields=(
                'tipo_remision',
                'nro_remision',
                'fecha_prometida_entrega',
                'entregado',
            ),
            form=RemisionCotizacionForm,
            can_delete=True,
            can_order=True,
            extra=1
        )

        TareaFormSet = inlineformset_factory(
            parent_model=Cotizacion,
            model=TareaCotizacion,
            fields=('nombre',
                    'descripcion',
                    'fecha_inicial',
                    'fecha_final',
                    'esta_finalizada'
                    ),
            form=TareaCotizacionForm,
            can_delete=True,
            can_order=True,
            extra=1
        )

        remision_formset = RemisionFormSet(instance=self.get_object())
        tarea_formset = TareaFormSet(instance=self.get_object())

        context["tareas"] = tarea_formset
        helper_tarea = TareaCotizacionFormHelper()
        context["helper_tarea"] = helper_tarea

        context["remisiones"] = remision_formset
        helper_remision = RemisionCotizacionFormHelper()
        context["helper_remision"] = helper_remision

        context["comentario_form"] = ComentarioCotizacionForm(initial={"cotizacion": self.get_object()})
        return context

    def get(self, request, *args, **kwargs):
        if self.get_object().en_edicion:
            return redirect(reverse('cotizaciones:cotizador'))
        return super().get(request, *args, **kwargs)


class CotizacionRemisionView(SingleObjectMixin, SelectRelatedMixin, FormView):
    template_name = "cotizaciones/cotizacion_detail.html"
    form_class = RemisionCotizacionForm
    model = Cotizacion
    select_related = (
        'usuario',
        'usuario__user_extendido',
        'usuario__user_extendido__colaborador'
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        RemisionFormSet = inlineformset_factory(
            parent_model=Cotizacion,
            model=RemisionCotizacion,
            fields=(
                'tipo_remision',
                'nro_remision',
                'fecha_prometida_entrega',
                'entregado',
            ),
            form=RemisionCotizacionForm,
            can_delete=True,
            can_order=True,
            extra=1
        )

        TareaFormSet = inlineformset_factory(
            parent_model=Cotizacion,
            model=TareaCotizacion,
            fields=('nombre',
                    'descripcion',
                    'fecha_inicial',
                    'fecha_final',
                    'esta_finalizada'
                    ),
            form=TareaCotizacionForm,
            can_delete=True,
            can_order=True,
            extra=1
        )

        if self.request.method == "POST":
            cotizacion = self.get_object()

            es_cambiar_tareas = self.request.POST.get('cambiar_tareas')
            es_cambiar_remision = self.request.POST.get('cambiar_remision')
            es_rechazada = self.request.POST.get('rechazar')
            es_aceptada = self.request.POST.get('aceptada')
            es_completada = self.request.POST.get('completada')
            es_recibida = self.request.POST.get('recibida')

            if es_rechazada:
                cotizacion.estado = 'ELI'
                cotizacion.save()

            if es_aceptada:
                cotizacion.estado = 'PRO'
                cotizacion.save()

            if es_completada:
                cotizacion.estado = 'FIN'
                if cotizacion.mis_remisiones.count() > 0:
                    cotizacion.save()
                else:
                    mensaje = "No es posible terminar la cotización %s sin relacionar ninguna remisión" % (
                        cotizacion.nro_cotizacion)
                    messages.add_message(self.request, messages.ERROR, mensaje)

            if es_recibida:
                cotizacion.estado = 'REC'
                cotizacion.save()

            remision_formset = RemisionFormSet(instance=cotizacion)
            tarea_formset = TareaFormSet(instance=cotizacion)
            if es_cambiar_tareas:
                tarea_formset = TareaFormSet(self.request.POST, instance=cotizacion)
                if tarea_formset.is_valid():
                    tarea_formset.save()
                    tarea_formset = TareaFormSet(instance=cotizacion)

            if es_cambiar_remision:
                remision_formset = RemisionFormSet(self.request.POST, instance=cotizacion)
                if remision_formset.is_valid():
                    if remision_formset.is_valid():
                        remision_formset.save()
                        remision_formset = RemisionFormSet(instance=cotizacion)

        context["object"] = self.get_object()

        context["tareas"] = tarea_formset
        helper_tarea = TareaCotizacionFormHelper()
        context["helper_tarea"] = helper_tarea

        context["remisiones"] = remision_formset
        helper_remision = RemisionCotizacionFormHelper()
        context["helper_remision"] = helper_remision

        context["comentario_form"] = ComentarioCotizacionForm(initial={"cotizacion": self.get_object()})
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)


class EditarCotizacion(View):
    def post(self, request, *args, **kwargs):
        usuario = self.request.user
        coti_id = request.POST.get('editar')
        cotizacion = get_object_or_404(Cotizacion, pk=coti_id)
        cotizacion.en_edicion = True
        Cotizacion.objects.filter(actualmente_cotizador=True, usuario=usuario).update(actualmente_cotizador=False)
        cotizacion.actualmente_cotizador = True
        cotizacion.save()
        return redirect(reverse('cotizaciones:cotizador'))


class ComentarCotizacionView(View):
    def post(self, request, *args, **kwargs):
        cotizacion = Cotizacion.objects.get(pk=request.POST.get('cotizacion'))
        comentario = ComentarioCotizacion(
            usuario=self.request.user,
            comentario=request.POST.get('comentario'),
            cotizacion=cotizacion
        )
        comentario.save()
        return redirect(cotizacion)


class CotizacionView(View):
    def get(self, request, *args, **kwargs):
        view = CotizacionDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = CotizacionRemisionView.as_view()
        return view(request, *args, **kwargs)


class EmailPrueba(View):
    def get(self, request, *args, **kwargs):
        connection = get_connection(host=settings.EMAIL_HOST_ODECO,
                                    port=settings.EMAIL_PORT_ODECO,
                                    username=settings.EMAIL_HOST_USER_ODECO,
                                    password=settings.EMAIL_HOST_PASSWORD_ODECO,
                                    use_tls=settings.EMAIL_USE_TLS_ODECO
                                    )

        obj = Cotizacion.objects.first()

        markdown = mistune.Markdown()
        if obj.estado == "INI":
            obj.razon_social = self.request.POST.get('razon_social')
            obj.nombres_contacto = self.request.POST.get('nombres_contacto')
            obj.apellidos_contacto = self.request.POST.get('apellidos_contacto')
            obj.email = self.request.POST.get('email')
            obj.nro_contacto = self.request.POST.get('nro_contacto')
            obj.observaciones = markdown(self.request.POST.get('observaciones'))
            obj.ciudad = self.request.POST.get('ciudad')
            obj.pais = self.request.POST.get('pais')
            obj.nro_cotizacion = "%s - %s" % ('CB', obj.id)
            obj.fecha_envio = timezone.now()
            obj.estado = "ENV"
            obj.save()

        esta_en_edicion = obj.en_edicion
        if obj.en_edicion:
            obj.en_edicion = False
            obj.fecha_envio = timezone.now()
            obj.version += 1
            obj.save()

        from_email = "ODECOPACK / COMPONENTES <%s>" % (settings.EMAIL_HOST_USER_ODECO)
        # to = obj.email
        to = "fabio.garcia.sanchez@gmail.com"
        subject = "Ignorara Correo de Prueba Fabio"
        if esta_en_edicion:
            subject = "%s, version %s" % (subject, obj.version)

        ctx = {
            'object': obj,
        }

        user = User.objects.get(username=request.user)

        try:
            colaborador = Colaborador.objects.get(usuario__user=user)
        except Colaborador.DoesNotExist:
            colaborador = None

        if colaborador:
            if colaborador.foto_perfil:
                url_avatar = colaborador.foto_perfil.url
                ctx['avatar'] = url_avatar

        nombre_archivo_cotizacion = "Cotizacion Odecopack - CB %s.pdf" % (obj.id)
        if esta_en_edicion:
            ctx['version'] = obj.version
            nombre_archivo_cotizacion = "Cotizacion Odecopack - CB %s ver %s.pdf" % (obj.id, obj.version)

        hora = int(timezone.localtime(timezone.now()).hour)
        if hora > 6 and hora < 12:
            tiempo_saludo = "Buenos días"
        elif hora > 11 and hora < 18:
            tiempo_saludo = "Buenas tardes"
        else:
            tiempo_saludo = "Buenas noches"

        saludo = "%s, mi nombre es %s" % (tiempo_saludo, colaborador.usuario.user.get_full_name())

        text_content = "%s.<br>%s %s.<br>%s." % (
            saludo,
            "Adjunto, en pdf, envío la cotización solicitada con número CB ",
            obj.id,
            "Yo y Odecopack, le deseamos un felíz día. Gracias por preferirnos"
        )

        html_content = get_template('cotizaciones/emails/cotizacion.html').render(Context(ctx))

        output = BytesIO()
        HTML(string=html_content).write_pdf(target=output)
        msg = EmailMultiAlternatives(subject, text_content, from_email, to=[to], bcc=[user.email],
                                     connection=connection)
        msg.content_subtype = "html"
        msg.attach(nombre_archivo_cotizacion, output.getvalue(), 'application/pdf')
        msg.send()
        output.close()
        return redirect(obj)


class CotizacionEmailView(EnviarCotizacionMixin, View):
    def post(self, request, *args, **kwargs):
        id = self.request.POST.get('id')
        cotizacion_actual = Cotizacion.objects.get(id=id)
        self.enviar_cotizacion(cotizacion_actual, self.request.user)
        return redirect(cotizacion_actual)


class TareaListView(SelectRelatedMixin, ListView):
    model = TareaCotizacion
    select_related = ['cotizacion', 'cotizacion__usuario']
    template_name = 'cotizaciones/tarea_list.html'

    def get_queryset(self):
        query = self.request.GET.get("buscado")
        user = self.request.user

        qs = super().get_queryset()

        full_permisos = user.has_perm('cotizaciones.full_cotizacion')
        if full_permisos:
            user = None

        if not query:
            query = ""

        qs = qs.filter(
            Q(esta_finalizada=False) &
            Q(cotizacion__in=(Cotizacion.estados.activo(usuario=user)))
        ).distinct().order_by('fecha_final')
        return qs


class RemisionListView(SelectRelatedMixin, ListView):
    model = RemisionCotizacion
    select_related = ['cotizacion', 'cotizacion__usuario']
    template_name = 'cotizaciones/remision_list.html'

    def get_queryset(self):
        query = self.request.GET.get("buscado")
        user = self.request.user
        qs = super().get_queryset()

        full_permisos = user.has_perm('cotizaciones.full_cotizacion')
        if full_permisos:
            user = None

        if not query:
            query = ""

        qs = qs.filter(
            Q(entregado=False) &
            Q(cotizacion__in=(Cotizacion.estados.activo(usuario=user)))
        ).distinct().order_by('fecha_prometida_entrega')
        return qs


class CotizacionesListView(SelectRelatedMixin, ListView):
    model = Cotizacion
    template_name = 'cotizaciones/cotizacion_list.html'

    def get_queryset(self):
        query = self.request.GET.get("buscado")

        current_user = self.request.user
        qsFinal = None

        qs = Cotizacion.estados.activo().exclude(estado='INI')

        if self.kwargs.get("tipo") == '2':
            qs = Cotizacion.estados.completado()

        if self.kwargs.get("tipo") == '3':
            qs = Cotizacion.estados.rechazado()

        qs = qs.select_related(
            'usuario',
            'cliente_biable',
            'ciudad_despacho',
            'ciudad_despacho__departamento',
            'ciudad_despacho__departamento__pais'
        ).prefetch_related(
            'mis_remisiones',
            'mis_remisiones__factura_biable'
        )

        if query:
            qs = Cotizacion.objects.all().select_related(
                'usuario',
                'cliente_biable',
                'ciudad_despacho',
                'ciudad_despacho__departamento',
                'ciudad_despacho__departamento__pais'
            ).prefetch_related(
                'mis_remisiones',
                'mis_remisiones__factura_biable'
            )
            qs = qs.filter(
                Q(nombres_contacto__icontains=query) |
                Q(cliente_biable__nombre__icontains=query) |
                Q(nro_cotizacion__icontains=query) |
                Q(ciudad__icontains=query) |
                Q(razon_social__icontains=query) |
                Q(items__item__descripcion_estandar__icontains=query) |
                Q(items__item__descripcion_comercial__icontains=query) |
                Q(items__item__referencia__icontains=query) |
                Q(items__banda__descripcion_estandar__icontains=query) |
                Q(items__banda__descripcion_comercial__icontains=query) |
                Q(items__banda__referencia__icontains=query) |
                Q(items__articulo_catalogo__referencia__icontains=query) |
                Q(items__articulo_catalogo__nombre__icontains=query)
            )

        if not current_user.has_perm('biable.reporte_ventas_todos_vendedores'):
            usuario = get_object_or_404(Colaborador, usuario__user=current_user)
            users = usuario.subalternos.all().values('usuario__user')
            qsFinal = qs.filter(
                Q(usuario=current_user) |
                Q(usuario__in=users)
            ).distinct().order_by('-id').distinct()
        else:
            qsFinal = qs.order_by('-id').distinct()
        return qsFinal

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_busqueda"] = BusquedaCotiForm(self.request.GET or None)
        return context
