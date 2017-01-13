from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from braces.views import SelectRelatedMixin, PrefetchRelatedMixin

from .models import EnvioTransportadoraTCC
from .forms import EnvioTccForm
# Create your views here.

class EnvioTransportadoraTCCUpdateView(UpdateView):
    template_name = 'despachos_mercancias/envio_tcc_update.html'
    model = EnvioTransportadoraTCC
    form_class = EnvioTccForm

class EnvioTransportadoraTCCDetailView(PrefetchRelatedMixin,SelectRelatedMixin,DetailView):
    template_name = 'despachos_mercancias/envio_tcc_detail.html'
    model = EnvioTransportadoraTCC
    select_related = ["ciudad","ciudad__departamento","cliente"]
    prefetch_related = ["facturas","facturas__cliente","facturas__vendedor"]

class EnvioTransportadoraTCCReporteView(SelectRelatedMixin,TemplateView):
    template_name = 'despachos_mercancias/reporte_seguimiento.html'
    select_related = ["ciudad", "ciudad__departamento","cliente"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = EnvioTransportadoraTCC.pendientes
        context["boom"] = qs.boom().select_related("ciudad", "ciudad__departamento","cliente")
        context["entrega"] = qs.entrega().select_related("ciudad", "ciudad__departamento","cliente")
        context["entrega_boom"] = qs.entrega_boom().select_related("ciudad", "ciudad__departamento","cliente")
        return context

