from decimal import Decimal

from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.template.loader import render_to_string, get_template
from django.urls import reverse
from django.db.models import Q
from django.template import Context
from django.conf import settings
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.views import View
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import ListView
from django.views.generic import DetailView
from django.forms import inlineformset_factory
from django.utils import timezone

from .models import (
    ItemCotizacion,
    Cotizacion,
    RemisionCotizacion,
    TareaCotizacion
)
from productos.models import Producto
from .forms import (
    BusquedaCotiForm,
    RemisionCotizacionForm,
    RemisionCotizacionFormHelper,
    TareaCotizacionForm,
    TareaCotizacionFormHelper
)


class CotizacionDetailView(DetailView):
    model = Cotizacion

    def get_object(self, queryset=None):
        obj = self.model.objects \
            .select_related('usuario', 'usuario__user_extendido', 'usuario__user_extendido__colaborador') \
            .prefetch_related('items__item', 'items__forma_pago', 'mis_tareas') \
            .get(id=self.kwargs["pk"])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        RemisionFormSet = inlineformset_factory(
            parent_model=Cotizacion,
            model=RemisionCotizacion,
            fields=('nro_factura',
                    'nro_remision',
                    'fecha_prometida_entrega',
                    'entregado',
                    ),
            form=RemisionCotizacionForm,
            can_delete=True,
            can_order=True,
            extra=2
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
        return context


class CotizacionRemisionView(SingleObjectMixin, FormView):
    template_name = "cotizaciones/cotizacion_detail.html"
    form_class = RemisionCotizacionForm
    model = Cotizacion

    def get_object(self, queryset=None):
        obj = self.model.objects \
            .select_related('usuario', 'usuario__user_extendido', 'usuario__user_extendido__colaborador') \
            .prefetch_related('items__item', 'items__forma_pago', 'mis_tareas') \
            .get(id=self.kwargs["pk"])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        RemisionFormSet = inlineformset_factory(
            parent_model=Cotizacion,
            model=RemisionCotizacion,
            fields=('nro_factura',
                    'nro_remision',
                    'fecha_prometida_entrega',
                    'entregado',
                    ),
            form=RemisionCotizacionForm,
            can_delete=True,
            can_order=True,
            extra=2
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
            print(self.request.POST)
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
                cotizacion.save()

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
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('cotizaciones:detalle_cotizacion', kwargs={'pk': self.object.pk})


class CotizacionView(View):
    def get(self, request, *args, **kwargs):
        view = CotizacionDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = CotizacionRemisionView.as_view()
        return view(request, *args, **kwargs)


class CotizacionEmailView(View):
    def post(self, request, *args, **kwargs):
        pk = kwargs['pk']
        obj = Cotizacion.objects.get(pk=pk)
        if obj.estado == "INI":
            obj.razon_social = self.request.POST.get('razon_social')
            obj.nombres_contacto = self.request.POST.get('nombres_contacto')
            obj.apellidos_contacto = self.request.POST.get('apellidos_contacto')
            obj.email = self.request.POST.get('email')
            obj.nro_contacto = self.request.POST.get('nro_contacto')
            obj.ciudad = self.request.POST.get('ciudad')
            obj.pais = self.request.POST.get('pais')
            obj.nro_cotizacion = "%s - %s" % ('CB', obj.id)
            obj.fecha_envio = timezone.now()
            obj.estado = "ENV"
            obj.save()

            subject, from_email, to = "%s - %s" % (
                'Cotizacion', obj.nro_cotizacion), settings.EMAIL_HOST_USER, obj.email

            ctx = {
                'object': obj,
            }

            text_content = render_to_string('cotizaciones/emails/cotizacion.html', ctx)
            html_content = get_template('cotizaciones/emails/cotizacion.html').render(Context(ctx))
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        return redirect(obj)


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
        ).order_by('fecha_final')
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
        ).order_by('fecha_prometida_entrega')
        return qs


class CotizacionesListView(ListView):
    model = Cotizacion

    def get_queryset(self):
        query = self.request.GET.get("buscado")
        user = self.request.user

        full_permisos = user.has_perm('cotizaciones.full_cotizacion')
        if full_permisos:
            user = None

        if not query:
            query = ""

        qs = Cotizacion.estados.activo(usuario=user).filter(
            Q(nombres_contacto__icontains=query) |
            Q(nro_cotizacion__icontains=query) |
            Q(ciudad__icontains=query) |
            Q(razon_social__icontains=query) |
            Q(items__item__descripcion_estandar__icontains=query) |
            Q(items__item__referencia__icontains=query)
        ).order_by('-total').distinct()
        return qs

    def get_context_data(self, **kwargs):

        # qs = ItemCotizacion.objects.filter(
        #     cotizacion__estado__exact="ENV"
        # )
        # print(qs)

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
