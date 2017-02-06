from braces.views import LoginRequiredMixin
from braces.views import PrefetchRelatedMixin
from braces.views import SelectRelatedMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView
from django.views.generic.detail import DetailView

from cotizaciones.models import (
    Cotizacion)
from biable.models import Cartera, VendedorBiable
from .forms import SeguimientoTareaForm
from usuarios.models import Colaborador
from .models import (
    TareaEnvioTCC,
    TareaCartera,
    TareaCotizacion,
    SeguimientoCotizacion,
    SeguimientoCartera,
    SeguimientoEnvioTCC,
    TrabajoDiario
)
from despachos_mercancias.models import EnvioTransportadoraTCC
from indicadores.mixins import IndicadorMesMixin


# Create your views here.

# region Trabajo Diario
class TrabajoDiaView(IndicadorMesMixin, LoginRequiredMixin, TemplateView):
    template_name = 'trabajo_diario/trabajo_dia.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        fecha_hoy = timezone.now().date()

        if usuario.has_perm('trabajo_diario.ver_trabajo_diario'):
            try:
                print('entro a existe')
                trabajo_diario = TrabajoDiario.objects.get(created__date=fecha_hoy, usuario=usuario)
            except TrabajoDiario.DoesNotExist:
                print('entro a no existe')
                trabajo_diario = None

            if not trabajo_diario:
                print('entro trabajo diario')
                trabajo_diario = TrabajoDiario()
                trabajo_diario.usuario = usuario
                trabajo_diario.save()

                vendedores_biable = VendedorBiable.objects.filter(colaborador__usuario__user=usuario).distinct()

                if vendedores_biable.exists():
                    qsEnvios = EnvioTransportadoraTCC.pendientes.select_related('tarea').filter(
                        facturas__vendedor__in=vendedores_biable
                    ).distinct()
                    for envio in qsEnvios.all():
                        try:
                            tarea_envio = envio.tarea
                            tarea_envio.estado = 0
                        except TareaEnvioTCC.DoesNotExist:
                            tarea_envio = TareaEnvioTCC()
                            tarea_envio.envio = envio
                        tarea_envio.descripcion = tarea_envio.get_descripcion_tarea()
                        tarea_envio.trabajo_diario = trabajo_diario
                        tarea_envio.save()

                    qsCotizacion = Cotizacion.estados.activo().select_related('tarea').filter(
                        created__date__lt=fecha_hoy,
                        usuario=usuario).order_by(
                        '-total')
                    for cotizacion in qsCotizacion.all():
                        try:
                            tarea_cotizacion = cotizacion.tarea
                            tarea_cotizacion.estado = 0
                        except TareaCotizacion.DoesNotExist:
                            tarea_cotizacion = TareaCotizacion()
                            tarea_cotizacion.cotizacion = cotizacion
                        tarea_cotizacion.descripcion = tarea_cotizacion.get_descripcion_tarea()
                        tarea_cotizacion.trabajo_diario = trabajo_diario
                        tarea_cotizacion.save()

                        qsCartera = Cartera.objects.select_related('factura', 'factura__tarea').filter(
                            esta_vencido=True,
                            vendedor__in=vendedores_biable).distinct().order_by(
                            "-dias_vencido")
                        for cartera in qsCartera.all():
                            factura = cartera.factura
                            if factura:
                                try:
                                    tarea_cartera = factura.tarea
                                    tarea_cartera.estado = 0
                                except TareaCartera.DoesNotExist:
                                    tarea_cartera = TareaCartera()
                                    tarea_cartera.factura = factura
                                tarea_cartera.descripcion = "%s vencida por %s dia(s)" % (
                                    tarea_cartera.get_descripcion_tarea(), cartera.dias_vencido)
                                tarea_cartera.trabajo_diario = trabajo_diario
                                tarea_cartera.save()

                trabajo_diario.set_actualizar_seguimiento_trabajo()

            context['carteras'] = trabajo_diario.tareas_cartera
            context['envios_tcc'] = trabajo_diario.tareas_envios_tcc
            context['cotizaciones'] = trabajo_diario.tareas_cotizacion
            context["porcentaje_tareas_atendidas"] = trabajo_diario.porcentaje_atendido

        if not usuario.has_perm('biable.reporte_ventas_todos_vendedores'):
            try:
                subalternos = Colaborador.objects.get(usuario__user=usuario).subalternos.values(
                    'usuario__user').all()
            except Colaborador.DoesNotExist:
                subalternos = None
        else:
            subalternos = Colaborador.objects.values('usuario__user')
        if subalternos:
            trabajo_diario_subalternos = TrabajoDiario.objects.select_related('usuario').filter(
                Q(usuario__in=subalternos) &
                Q(created__date__exact=fecha_hoy) &
                ~Q(usuario=usuario)
            ).distinct()
            context['trabajo_diario_subalternos'] = trabajo_diario_subalternos

        return context


# endregion

# region Tareas Diarias
class TareaUpdateView(PrefetchRelatedMixin, SelectRelatedMixin, UpdateView):
    template_name = 'trabajo_diario/tarea_detail.html'
    prefetch_related = ["seguimientos__usuario"]
    select_related = ["trabajo_diario", "trabajo_diario__usuario"]
    fields = ('estado',)

    def crear_nuevo_seguimiento(self, observacion, tarea, usuario):
        pass

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.object.trabajo_diario.usuario_id == self.request.user.id:
            context["observacion_form"] = SeguimientoTareaForm(initial={'estado': self.object.estado})
        return context

    def post(self, request, *args, **kwargs):
        estado = request.POST.get('estado')
        self.object = self.get_object()

        observacion = request.POST.get('observacion')
        if observacion:
            seguimiento = self.crear_nuevo_seguimiento(observacion, self.object, self.request.user)
            print('entro')
            seguimiento.save()

        if estado != self.object.estado:
            self.object.estado = estado
            self.object.save()

        return redirect(reverse('index'))


class TareaCotizacionDetailView(TareaUpdateView):
    model = TareaCotizacion

    def crear_nuevo_seguimiento(self, observacion, tarea, usuario):
        seguimiento = SeguimientoCotizacion(
            observacion=observacion,
            tarea=tarea,
            usuario=usuario
        )
        return seguimiento


class TareaEnvioTccDetailView(TareaUpdateView):
    model = TareaEnvioTCC

    def crear_nuevo_seguimiento(self, observacion, tarea, usuario):
        seguimiento = SeguimientoEnvioTCC(
            observacion=observacion,
            tarea=tarea,
            usuario=usuario
        )
        return seguimiento


class TareaCarteraDetailView(TareaUpdateView):
    model = TareaCartera

    def crear_nuevo_seguimiento(self, observacion, tarea, usuario):
        seguimiento = SeguimientoCartera(
            observacion=observacion,
            tarea=tarea,
            usuario=usuario
        )
        return seguimiento


class TrabajoDiarioDetailView(SelectRelatedMixin, PrefetchRelatedMixin, DetailView):
    model = TrabajoDiario
    select_related = ["usuario"]
    prefetch_related = ["tareas_cotizacion", "tareas_envios_tcc", "tareas_cartera"]
    template_name = 'trabajo_diario/trabajo_diario_por_vendedor.html'

# endregion
