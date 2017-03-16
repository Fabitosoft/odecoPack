from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Q
from django.views import View
from django.views.generic import UpdateView
from django.views.generic.list import ListView
from django.forms import inlineformset_factory
from django.contrib import messages

from braces.views import SelectRelatedMixin, LoginRequiredMixin

from usuarios.mixins import UsuariosMixin
from ..models import (
    Cotizacion,
    RemisionCotizacion,
    TareaCotizacion,
)

from ..forms import (
    BusquedaCotiForm,
    RemisionCotizacionForm,
    RemisionCotizacionFormHelper,
    TareaCotizacionForm,
    TareaCotizacionFormHelper,
    ComentarioCotizacionForm,
    CambiarResponsableCotizacionForm)
from ..mixins import EnviarCotizacionMixin


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
        user = self.request.user
        qs = super().get_queryset()
        qs = qs.filter(
            esta_finalizada=False
        ).distinct().order_by('fecha_final')

        full_permisos = user.has_perm('cotizaciones.full_cotizacion')
        if not full_permisos:
            qs = qs.filter(cotizacion__in=(Cotizacion.estados.activo().filter(usuario=user)))

        return qs


class RemisionListView(SelectRelatedMixin, ListView):
    model = RemisionCotizacion
    select_related = ['cotizacion', 'cotizacion__usuario', 'factura_biable']
    template_name = 'cotizaciones/remision_list.html'

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        qs = qs.filter(
            entregado=False
        ).distinct().order_by('fecha_prometida_entrega')

        full_permisos = user.has_perm('cotizaciones.full_cotizacion')
        if not full_permisos:
            qs = qs.filter(cotizacion__in=(Cotizacion.estados.activo().filter(usuario=user)))

        return qs


class CotizacionesListView(LoginRequiredMixin, UsuariosMixin, SelectRelatedMixin, ListView):
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
            'creado_por',
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
                Q(items__articulo_catalogo__nombre__icontains=query) |
                Q(usuario__username__icontains=query) |
                Q(usuario__first_name=query)
            )

        if not current_user.has_perm('biable.reporte_ventas_todos_vendedores'):
            subalternos = self.get_sub_alternos(current_user)
            qsFinal = qs.filter(
                Q(usuario=current_user) |
                Q(usuario__in=subalternos)
            ).distinct().order_by('-id').distinct()
        else:
            qsFinal = qs.order_by('-id').distinct()
        return qsFinal

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_busqueda"] = BusquedaCotiForm(self.request.GET or None)
        return context


class CotizacionView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        view = CotizacionDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.request.POST.get('form_estado'):
            view = CotizacionCambiarEstadoView.as_view()
        if self.request.POST.get('form_comentar'):
            view = CotizacionComentarView.as_view()
        if self.request.POST.get('form_remision'):
            view = CotizacionRemisionView.as_view()
        if self.request.POST.get('form_tareas'):
            view = CotizacionTareaView.as_view()
        if self.request.POST.get('asignar_vendedor'):
            view = CotizacionAsignarVendedorView.as_view()
        return view(request, *args, **kwargs)


class FormSetsCotizacionMixin(object):
    def get_formset_remision(self):
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
        return RemisionFormSet(self.request.POST or None, instance=self.object)

    def get_formset_tareas(self):
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
        return TareaFormSet(self.request.POST or None, instance=self.object)


class CotizacionDetailView(UsuariosMixin, SelectRelatedMixin, FormSetsCotizacionMixin, UpdateView):
    template_name = 'cotizaciones/cotizacion/cotizacion_detalle.html'
    select_related = [
        'cliente_biable',
        'ciudad_despacho',
        'ciudad_despacho',
        'ciudad_despacho__departamento',
        'ciudad_despacho__departamento__pais',
        'tarea_diaria_cotizacion'
    ]
    model = Cotizacion
    context_object_name = 'cotizacion'
    fields = '__all__'

    def get_success_url(self):
        return redirect('cotizaciones:detalle_cotizacion', {'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        initial = {"cotizacion": self.object, "usuario": self.request.user}
        context["comentario_form"] = ComentarioCotizacionForm(initial=initial)

        remision_formset = self.get_formset_remision()
        tarea_formset = self.get_formset_tareas()

        context["tareas"] = tarea_formset
        context["asignar_vendedor_form"] = CambiarResponsableCotizacionForm(instance=self.object)
        helper_tarea = TareaCotizacionFormHelper()
        context["helper_tarea"] = helper_tarea

        context["remisiones"] = remision_formset
        helper_remision = RemisionCotizacionFormHelper()
        context["helper_remision"] = helper_remision

        context["puede_modificar"] = False
        usuario = self.request.user
        if not usuario.is_superuser:
            subalternos = self.get_sub_alternos(usuario)
            if self.object.usuario in subalternos or self.object.usuario == usuario:
                context["puede_modificar"] = True
        else:
            context["puede_modificar"] = True
        return context


class CotizacionCambiarEstadoView(CotizacionDetailView):
    def post(self, request, *args, **kwargs):
        cambiar_estado = self.request.POST.get('form_estado')
        cotizacion = self.get_object()
        if cambiar_estado:
            self.cambiar_estado(cambiar_estado, cotizacion)
        return redirect(cotizacion)

    def cambiar_estado(self, cambiar_estado, cotizacion):
        if cambiar_estado == "Rechazar":
            cotizacion.estado = 'ELI'
            cotizacion.save()

        if cambiar_estado == "Aceptada":
            cotizacion.estado = 'PRO'
            cotizacion.save()

        if cambiar_estado == "Completada":
            cotizacion.estado = 'FIN'
            if cotizacion.mis_remisiones.count() > 0:
                cotizacion.save()
            else:
                mensaje = "No es posible terminar la cotización %s sin relacionar ninguna remisión" % (
                    cotizacion.nro_cotizacion)
                messages.add_message(self.request, messages.ERROR, mensaje)

        if cambiar_estado == "Recibida":
            cotizacion.estado = 'REC'
            cotizacion.save()


class CotizacionComentarView(CotizacionDetailView):
    def post(self, request, *args, **kwargs):
        formulario = ComentarioCotizacionForm(self.request.POST)
        formulario.save()
        cotizacion = self.get_object()
        return redirect(cotizacion)


class CotizacionRemisionView(CotizacionDetailView):
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        remision_formset = self.get_formset_remision()
        if remision_formset.is_valid():
            remision_formset.save()
        return redirect(self.object, self.request.POST)


class CotizacionTareaView(CotizacionDetailView):
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        tarea_formset = self.get_formset_tareas()
        if tarea_formset.is_valid():
            tarea_formset.save()
        return redirect(self.object, self.request.POST)


class CotizacionAsignarVendedorView(CotizacionDetailView):
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CambiarResponsableCotizacionForm(self.request.POST, instance=self.object)
        form.save()
        return redirect('cotizaciones:listar_cotizaciones')
