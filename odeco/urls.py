"""odeco URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views

from trabajo_diario.views import TrabajoDiaView

urlpatterns = [
    url(r'^$', TrabajoDiaView.as_view(), name='index'),
    url(r'^admin/', admin.site.urls),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^accounts/', include('registration.backends.default.urls')),
    # override the default urls
    url(r'^password/change/$',
        auth_views.password_change,
        name='password_change'),
    url(r'^password/change/done/$',
        auth_views.password_change_done,
        name='password_change_done'),
    url(r'^password/reset/$',
        auth_views.password_reset,
        name='password_reset'),
    url(r'^password/reset/done/$',
        auth_views.password_reset_done,
        name='password_reset_done'),
    url(r'^password/reset/complete/$',
        auth_views.password_reset_complete,
        name='password_reset_complete'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.password_reset_confirm,
        name='password_reset_confirm'),
    url(r'^cotizaciones/', include('cotizaciones.urls', namespace="cotizaciones")),
    url(r'^bandas/', include('bandas.urls', namespace="bandas")),
    url(r'^indicadores/', include('indicadores.urls', namespace="indicadores")),
    url(r'^trabajo_diario/', include('trabajo_diario.urls', namespace="trabajo_diario")),
    url(r'^despacho_mercancia/', include('despachos_mercancias.urls', namespace="despacho_mercancia")),
    url(r'^biable/', include('biable.urls', namespace="biable")),
]

if settings.DEBUG:
    # import debug_toolbar
    # urlpatterns += [
    #     url(r'^__debug__/', include(debug_toolbar.urls)),
    # ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
