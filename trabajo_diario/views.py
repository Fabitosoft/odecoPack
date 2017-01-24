from braces.views import LoginRequiredMixin
from braces.views import SelectRelatedMixin
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView
from django.views.generic.detail import DetailView

from cotizaciones.models import (
    Cotizacion,
)
from biable.models import Cartera, VendedorBiable
from usuarios.models import Colaborador
from .models import TrabajoDia, TareaDiaria
from despachos_mercancias.models import EnvioTransportadoraTCC
from indicadores.mixins import IndicadorMesMixin


# Create your views here.
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
            fecha_hoy = timezone.localtime(timezone.now()).date()
            usuario = self.request.user

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
                )
                for envio in qsEnvios.all():
                    for factura in envio.facturas.all():
                        if factura.vendedor in vendedores_biable.all():
                            descripcion = '%s de envío de la factura %s-%s con estado "%s". Nro Seguimiento %s' % (
                                envio.get_numero_dias_desde_envio(), factura.tipo_documento, factura.nro_documento,
                                envio.get_estado_display(), envio.nro_tracking)
                            self.generacion_tarea_diaria("Seguimiento Envío", descripcion, trabajo_dia,
                                                         envio.get_absolute_url())

                qsCartera = Cartera.objects.filter(esta_vencido=True, vendedor__in=vendedores_biable.all()).order_by(
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
            )
            context['trabajo_diario_subalternos'] = trabajo_diario_subalternos

        return context

    def generacion_tarea_diaria(self, tipo, descripcion, trabajo_dia, url=None):
        tarea = TareaDiaria(tipo=tipo, descripcion=descripcion, mi_dia=trabajo_dia, url=url)
        tarea.save()


class TrabajoDiarioDetailView(SelectRelatedMixin, DetailView):
    model = TrabajoDia
    select_related = ["usuario"]
    template_name = 'trabajo_diario/trabajo_diario_detail.html'
