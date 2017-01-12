from django.conf.urls import url

from .views import (
    EnvioTransportadoraTCCUpdateView,
    EnvioTransportadoraTCCDetailView
)

urlpatterns = [
    url(r'envio_update/(?P<pk>[0-9]+)/$', EnvioTransportadoraTCCUpdateView.as_view(), name='envio-update'),
    url(r'envio_detail/(?P<pk>[0-9]+)/$', EnvioTransportadoraTCCDetailView.as_view(), name='envio-detail'),
]
