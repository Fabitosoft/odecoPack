from django.views.generic.edit import UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .models import EnvioTransportadoraTCC
from .forms import EnvioTccForm
# Create your views here.

class EnvioTransportadoraTCCUpdateView(UpdateView):
    template_name = 'despachos_mercancias/envio_tcc_update.html'
    model = EnvioTransportadoraTCC
    form_class = EnvioTccForm

class EnvioTransportadoraTCCDetailView(DetailView):
    template_name = 'despachos_mercancias/envio_tcc_detail.html'
    model = EnvioTransportadoraTCC

class EnvioTransportadoraTCCReporteView(ListView):
    template_name = 'despachos_mercancias/reporte_seguimiento.html'
    queryset = EnvioTransportadoraTCC.pendientes