from decimal import Decimal, InvalidOperation
from io import BytesIO

from django.core.mail import get_connection
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404
from django.template.loader import get_template, render_to_string
from django.urls import reverse
from django.db.models import Q
from django.template import Context
from django.conf import settings
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import ListView
from django.views.generic import DetailView, FormView
from django.forms import inlineformset_factory
from django.utils import timezone
from django.contrib import messages

import mistune
from weasyprint import HTML

from braces.views import SelectRelatedMixin, PrefetchRelatedMixin

from listasprecios.forms import ProductoBusqueda
from biable.models import Colaborador
from .models import (
    ItemCotizacion,
    Cotizacion,
    RemisionCotizacion,
    TareaCotizacion,
    ComentarioCotizacion)
from productos.models import (
    Producto,
    ArticuloCatalogo
)
from bandas.models import Banda
from .models import FormaPago
from cotizaciones.forms import CotizacionForm
from .forms import (
    BusquedaCotiForm,
    RemisionCotizacionForm,
    RemisionCotizacionFormHelper,
    TareaCotizacionForm,
    TareaCotizacionFormHelper,
    ItemCotizacionOtrosForm,
    ComentarioCotizacionForm
)


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
        coti_id = request.POST.get('editar')
        cotizacion = get_object_or_404(Cotizacion, pk=coti_id)
        cotizacion.en_edicion = True
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
        print("Entro a enviar correo prueba")
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


class CotizacionEmailView(View):
    def post(self, request, *args, **kwargs):
        pk = kwargs['pk']
        obj = Cotizacion.objects.get(pk=pk)

        if obj.items.all().count() > 0:
            connection = get_connection(host=settings.EMAIL_HOST_ODECO,
                                        port=settings.EMAIL_PORT_ODECO,
                                        username=settings.EMAIL_HOST_USER_ODECO,
                                        password=settings.EMAIL_HOST_PASSWORD_ODECO,
                                        use_tls=settings.EMAIL_USE_TLS_ODECO
                                        )

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
            to = obj.email
            subject = "%s - %s" % ('Cotizacion', obj.nro_cotizacion)
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
            return redirect(obj)
        else:
            mensaje = "No se puede enviar una cotización sin items"
            messages.add_message(self.request, messages.ERROR, mensaje)
            return redirect(reverse('cotizaciones:cotizador'))


class TareaListView(ListView):
    model = TareaCotizacion
    template_name = 'cotizaciones/tarea_list.html'

    def get_queryset(self):
        query = self.request.GET.get("buscado")
        user = self.request.user

        full_permisos = user.has_perm('cotizaciones.full_cotizacion')
        if full_permisos:
            user = None

        if not query:
            query = ""

        qs = self.model.objects.filter(
            Q(esta_finalizada=False) &
            Q(cotizacion__in=(Cotizacion.estados.activo(usuario=user)))
        ).distinct().order_by('fecha_final')
        return qs


class RemisionListView(ListView):
    model = RemisionCotizacion
    template_name = 'cotizaciones/remision_list.html'

    def get_queryset(self):
        query = self.request.GET.get("buscado")
        user = self.request.user

        full_permisos = user.has_perm('cotizaciones.full_cotizacion')
        if full_permisos:
            user = None

        if not query:
            query = ""

        qs = self.model.objects.filter(
            Q(entregado=False) &
            Q(cotizacion__in=(Cotizacion.estados.activo(usuario=user)))
        ).distinct().order_by('fecha_prometida_entrega')
        return qs


class CotizacionesListView(ListView):
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

        if query:
            qs = Cotizacion.objects.all()
            qs = qs.filter(
                Q(nombres_contacto__icontains=query) |
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


class AddItemCantidad(SingleObjectMixin, View):
    model = ItemCotizacion

    def get(self, request, *args, **kwargs):
        delete = False
        error_cantidad = False
        actual_item_error = ""
        item_id = request.GET.get("item")
        item = ItemCotizacion.objects.get(id=item_id)
        try:
            qty = Decimal(request.GET.get("qty"))
            if qty <= 0:
                delete = True
                item.delete()
            else:
                item.cantidad = qty
                descuento = (item.precio * qty) * (item.porcentaje_descuento / 100)
                item.descuento = descuento
                item.total = (item.precio * qty) - descuento
                item.save()
            total_linea = round(item.total, 2)
            total_cotizacion = round(item.cotizacion.total, 2)
        except InvalidOperation as e:
            error_cantidad = True
            actual_item_error = item.get_nombre_item()
            total_linea = "ERROR CANTIDAD"
            total_cotizacion = "ERROR CANTIDAD"

        data = {
            "error_cantidad": error_cantidad,
            "actual_item_error": actual_item_error,
            "deleted": delete,
            "total_line": total_linea,
            "descuento": round(item.descuento, 2),
            "descuento_total": round(item.cotizacion.descuento, 2),
            "total_cotizacion": total_cotizacion
        }

        return JsonResponse(data)


class CambiarDiaEntregaView(SingleObjectMixin, View):
    model = ItemCotizacion

    def get(self, request, *args, **kwargs):
        delete = False
        item_id = request.GET.get("item")
        item = ItemCotizacion.objects.get(id=item_id)
        dias = Decimal(request.GET.get("dias"))

        item.dias_entrega = dias
        item.save()

        data = {
            "dias": item.dias_entrega
        }
        return JsonResponse(data)


class CambiarPorcentajeDescuentoView(SingleObjectMixin, View):
    model = ItemCotizacion

    def get(self, request, *args, **kwargs):
        item_id = request.GET.get("item")
        item = ItemCotizacion.objects.get(id=item_id)
        error_porcentaje = False
        error_mensaje = ""

        try:
            desc = Decimal(request.GET.get("desc"))
            if desc >= 0:
                item.porcentaje_descuento = desc
                descuento = (item.precio * item.cantidad) * (desc / 100)
                item.descuento = descuento
                item.total = (item.precio * item.cantidad) - descuento
                item.save()
                total_linea = round(item.total,2)
                descuento_linea = round(item.descuento,2)
                descuento_cotizacion = round(item.cotizacion.descuento,2)
                total_cotizacion = round(item.cotizacion.total,2)
            else:
                error_porcentaje = True
                error_mensaje = "Error en el porcentaje aplicado a %s, debe de ser un número igual o mayor a 1" % (
                    item.get_nombre_item())
                total_linea = "Error en % descuento"
                descuento_linea = "Error en % descuento"
                descuento_cotizacion = "Error en % descuento"
                total_cotizacion = "Error en % descuento"
        except InvalidOperation as e:
            error_porcentaje = True
            error_mensaje = "Error en el porcentaje aplicado a %s, debe ser un número valido" % (item.get_nombre_item())
            total_linea = "Error en % descuento"
            descuento_linea = "Error en % descuento"
            descuento_cotizacion = "Error en % descuento"
            total_cotizacion = "Error en % descuento"

        data = {
            "error_porcentaje": error_porcentaje,
            "error_mensaje": error_mensaje,
            "desc": round(item.porcentaje_descuento, 2),
            "total_line": total_linea,
            "descuento": descuento_linea,
            "descuento_total": descuento_cotizacion,
            "total_cotizacion": total_cotizacion
        }
        return JsonResponse(data)


class AddItem(SingleObjectMixin, View):
    model = ItemCotizacion

    def get(self, request, *args, **kwargs):
        coti_id = kwargs["cot_id"]
        item_id = kwargs["item_id"]
        precio = kwargs["precio"]
        forma_pago_id = kwargs["forma_pago"]
        tipo = int(kwargs["tipo"])
        if tipo == 1:
            item = ItemCotizacion.objects.filter(
                Q(item_id=item_id) &
                Q(cotizacion_id=coti_id)
            ).first()
        elif tipo == 2:
            item = ItemCotizacion.objects.filter(
                Q(articulo_catalogo_id=item_id) &
                Q(cotizacion_id=coti_id)
            ).first()
        else:
            item = ItemCotizacion.objects.filter(
                Q(banda_id=item_id) &
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

        if tipo == 1:
            item.item_id = item_id
        elif tipo == 2:
            item.articulo_catalogo_id = item_id
        else:
            item.banda_id = item_id

        item.precio = precio
        item.forma_pago_id = forma_pago_id
        item.total = float(precio) * float(item.cantidad)
        item.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class AddItemOtro(SingleObjectMixin, View):
    model = ItemCotizacion

    def post(self, request, *args, **kwargs):
        coti_id = request.POST.get('cotizacion_id')
        precio = request.POST.get('precio')
        nombre = request.POST.get('p_n_lista_descripcion')
        referencia = request.POST.get('p_n_lista_referencia')
        p_n_lista_unidad_medida = request.POST.get('p_n_lista_unidad_medida')
        item = ItemCotizacion.objects.filter(
            Q(p_n_lista_descripcion=nombre) &
            Q(cotizacion_id=coti_id)
        ).first()
        if not item:
            item = ItemCotizacion()
            item.cantidad = 1
            item.cotizacion_id = coti_id
        item.p_n_lista_descripcion = nombre
        item.p_n_lista_referencia = referencia
        item.p_n_lista_unidad_medida = p_n_lista_unidad_medida
        item.precio = precio
        item.total = precio * item.cantidad
        item.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# region Cotizador
class CotizacionFormView(FormView):
    def post(self, request, *args, **kwargs):
        cotizacion = Cotizacion.objects.filter(
            Q(usuario=self.request.user) &
            Q(en_edicion=True)
        ).last()

        if not cotizacion:
            try:
                cotizacion = Cotizacion.objects.get(
                    Q(usuario=self.request.user) &
                    Q(estado__exact="INI")
                )
            except Cotizacion.DoesNotExist:
                cotizacion = None

        if self.request.POST.get('crear') and not cotizacion:
            cotizacion = Cotizacion()
            cotizacion.usuario = self.request.user
            cotizacion.razon_social = self.request.POST.get('razon_social')
            cotizacion.nombres_contacto = self.request.POST.get('nombres_contacto')
            cotizacion.apellidos_contacto = self.request.POST.get('apellidos_contacto')
            cotizacion.email = self.request.POST.get('email')
            cotizacion.nro_contacto = self.request.POST.get('nro_contacto')
            cotizacion.ciudad = self.request.POST.get('ciudad')
            cotizacion.pais = self.request.POST.get('pais')
            cotizacion.fecha_envio = timezone.now()
            cotizacion.estado = "INI"
            cotizacion.save()
            cotizacion.nro_cotizacion = "%s - %s" % ('CB', cotizacion.id)
            cotizacion.save()

        if self.request.POST.get('descartar') and cotizacion:
            if cotizacion and cotizacion.en_edicion:
                cotizacion.en_edicion = False
                cotizacion.save()
            else:
                cotizacion.delete()
        return HttpResponseRedirect(reverse('cotizaciones:cotizador'))


class CotizadorTemplateView(TemplateView):
    template_name = 'cotizaciones/cotizador.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formu'] = ProductoBusqueda(self.request.GET or None)
        query = self.request.GET.get("buscar")
        if query:
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
            Q(en_edicion=True)
        ).last()

        if not cotizacion:
            try:
                cotizacion = Cotizacion.objects.get(
                    Q(usuario=self.request.user) &
                    Q(estado__exact="INI")
                )
            except Cotizacion.DoesNotExist:
                cotizacion = None

        if cotizacion:
            context["cotizacion_form"] = CotizacionForm(instance=cotizacion)
            context["cotizacion_form"].id = cotizacion.id

            if cotizacion.en_edicion:
                context["cotizacion_edit"] = cotizacion.nro_cotizacion

            context["cotizacion_id"] = cotizacion.id
            context["cotizacion_descuento"] = cotizacion.descuento
            context["cotizacion_total"] = cotizacion.total
            context["items_cotizacion"] = cotizacion.items.all()
            context["forma_item_otro"] = ItemCotizacionOtrosForm(initial={'cotizacion_id': cotizacion.id})
        else:
            context["cotizacion_form"] = CotizacionForm()

        context["forma_de_pago"] = self.request.GET.get('tipo')
        return context


class CotizadorView(View):
    def get(self, request, *args, **kwargs):
        view = CotizadorTemplateView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = CotizacionFormView.as_view()
        return view(request, *args, **kwargs)

# endregion
