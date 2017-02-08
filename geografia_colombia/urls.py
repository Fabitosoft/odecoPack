from django.conf.urls import url

from .views import CiudadAutocomplete

urlpatterns = [
    url(r'^ciudad-autocomplete/$', CiudadAutocomplete.as_view(), name='ciudad-autocomplete'),
]
