from braces.views import LoginRequiredMixin
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
from .models import TrabajoDia, TareaDiaria, TareaEnvioTCC, TareaCartera, TareaCotizacion, SeguimientoCotizacion, \
    SeguimientoCartera, SeguimientoEnvioTCC, TrabajoDiario
from despachos_mercancias.models import EnvioTransportadoraTCC
from indicadores.mixins import IndicadorMesMixin


# Create your views here.

# region Trabajo Diario
class TrabajoDiaView(IndicadorMesMixin, LoginRequiredMixin, TemplateView):
    template_name = 'trabajo_diario/trabajo_dia.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        fecha_hoy = timezone.localtime(timezone.now()).date()

        if usuario.has_perm('trabajo_diario.ver_trabajo_diario'):
            try:
                trabajo_diario = TrabajoDiario.objects.get(created__date=fecha_hoy, usuario=usuario)
            except TrabajoDiario.DoesNotExist:
                trabajo_diario = None

            if not trabajo_diario:
                print('entro no hay trabajo diario')
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
                            tarea_cartera.descripcion = "%s con %s dia(s) de vendido" % (
                                tarea_cartera.get_descripcion_tarea(), cartera.dias_vencido)
                            tarea_cartera.trabajo_diario = trabajo_diario
                            tarea_cartera.save()

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
class TareaUpdateView(UpdateView):
    template_name = 'trabajo_diario/tarea_detail.html'
    fields = ('estado',)

    def crear_nuevo_seguimiento(self, observacion, tarea, usuario):
        pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["observacion_form"] = SeguimientoTareaForm(initial={'estado': self.get_object().estado})
        return context

    def post(self, request, *args, **kwargs):
        estado = request.POST.get('estado')
        tarea = self.get_object()

        observacion = request.POST.get('observacion')
        if observacion:
            seguimiento = self.crear_nuevo_seguimiento(observacion, tarea, self.request.user)
            seguimiento.save()

        if estado != tarea.estado:
            tarea.estado = estado
            tarea.save()

        return redirect(reverse('trabajo_diario:tareas_hoy'))


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


class TrabajoDiarioDetailView(SelectRelatedMixin, DetailView):
    model = TrabajoDiario
    select_related = ["usuario"]
    template_name = 'trabajo_diario/trabajo_diario_detail.html'


# endregion

class TareaDiaUpdateView(UpdateView):
    template_name = 'trabajo_diario/tarea_dia_update.html'
    model = TareaDiaria
    fields = ['estado', 'observacion']

    def get_success_url(self):
        return reverse('trabajo_diario:lista_tareas')


class TareaDiaListView(IndicadorMesMixin, LoginRequiredMixin, TemplateView):
    template_name = 'trabajo_diario/trabajo_diario_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        fecha_hoy = timezone.localtime(timezone.now()).date()
        usuario = self.request.user
        vendedores_biable = VendedorBiable.objects.filter(colaborador__usuario__user=usuario)

        if usuario.has_perm('trabajo_diario.ver_trabajo_diario'):
            try:
                trabajo_dia = TrabajoDia.objects.get(created__date=fecha_hoy, usuario=usuario)
            except TrabajoDia.DoesNotExist:
                trabajo_dia = None

            if not trabajo_dia:
                trabajo_dia = TrabajoDia()
                trabajo_dia.usuario = usuario
                trabajo_dia.save()

                qsEnvios = EnvioTransportadoraTCC.pendientes.filter(
                    facturas__vendedor__in=vendedores_biable
                ).distinct()
                for envio in qsEnvios.all():
                    facturas = ""
                    for factura in envio.facturas.all():
                        if factura.vendedor in vendedores_biable.all():
                            facturas += " (%s-%s) " % (factura.tipo_documento, factura.nro_documento)
                    descripcion = '%s de envío de la(s) factura(s) %s con estado "%s". Nro Seguimiento %s' % (
                        envio.get_numero_dias_desde_envio(),
                        facturas,
                        envio.get_estado_display(),
                        envio.nro_tracking
                    )
                    self.generacion_tarea_diaria("Seguimiento Envío", descripcion, trabajo_dia,
                                                 envio.get_absolute_url())

                qsCartera = Cartera.objects.filter(esta_vencido=True,
                                                   vendedor__in=vendedores_biable.all()).distinct().order_by(
                    "-dias_vencido")
                qsCotizacion = Cotizacion.estados.activo().filter(created__date__lt=fecha_hoy,
                                                                  usuario=usuario).order_by(
                    '-total')
                for cartera in qsCartera.all():
                    descripcion = "%s tiene la factura %s-%s vencida por %s día(s)" % (
                        cartera.client.nombre, cartera.tipo_documento, cartera.nro_documento, cartera.dias_vencido)
                    self.generacion_tarea_diaria("Seguimiento Cartera Vencida", descripcion, trabajo_dia)

                for cotizacion in qsCotizacion.all():
                    descripcion = "Cotización %s %s con un valor de %s para %s" % (
                        cotizacion.get_estado_display(), cotizacion.nro_cotizacion, cotizacion.total,
                        cotizacion.razon_social)
                    self.generacion_tarea_diaria("Seguimiento Cotización", descripcion, trabajo_dia,
                                                 cotizacion.get_absolute_url())

                    for remision in cotizacion.mis_remisiones.filter(entregado=False).all():
                        descripcion = "Seguimiento a la entrega de la remision %s de la factura %s para %s" % (
                            remision.nro_remision, remision.nro_factura, cotizacion.razon_social)
                        self.generacion_tarea_diaria("Seguimiento Remisión", descripcion, trabajo_dia,
                                                     cotizacion.get_absolute_url())

                    for tarea in cotizacion.mis_tareas.filter(esta_finalizada=False).all():
                        descripcion = '"%s" de la cotización numero %s' % (
                            tarea.nombre, cotizacion.nro_cotizacion)
                        self.generacion_tarea_diaria("Seguimiento Tarea", descripcion, trabajo_dia,
                                                     cotizacion.get_absolute_url())
                trabajo_dia.set_actualizar_seguimiento_trabajo()

            context["porcentaje_tareas_atendidas"] = trabajo_dia.porcentaje_atendido
            context["seguimiento_tarea"] = trabajo_dia.mis_tareas.filter(tipo="Seguimiento Tarea")
            context["seguimiento_cotizacion"] = trabajo_dia.mis_tareas.filter(tipo="Seguimiento Cotización")
            context["seguimiento_remision"] = trabajo_dia.mis_tareas.filter(tipo="Seguimiento Remisión")
            context["seguimiento_envio"] = trabajo_dia.mis_tareas.filter(tipo="Seguimiento Envío")
            context["seguimiento_cartera"] = trabajo_dia.mis_tareas.filter(tipo="Seguimiento Cartera Vencida")

        if not usuario.has_perm('biable.reporte_ventas_todos_vendedores'):
            try:
                subalternos = Colaborador.objects.get(usuario__user=usuario).subalternos.values('usuario__user').all()
            except Colaborador.DoesNotExist:
                subalternos = None
        else:
            subalternos = Colaborador.objects.values('usuario__user')
        if subalternos:
            trabajo_diario_subalternos = TrabajoDia.objects.select_related('usuario').filter(
                Q(usuario__in=subalternos) &
                Q(created__date__exact=fecha_hoy) &
                ~Q(usuario=usuario)
            ).distinct()
            context['trabajo_diario_subalternos'] = trabajo_diario_subalternos

        return context

    def generacion_tarea_diaria(self, tipo, descripcion, trabajo_dia, url=None):
        tarea = TareaDiaria(tipo=tipo, descripcion=descripcion, mi_dia=trabajo_dia, url=url)
        tarea.save()
