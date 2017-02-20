from django.conf.urls import url

from .views import (
    VistaPrueba
)

urlpatterns = [
    url(r'^uno/', VistaPrueba.as_view(), name='prueba'),
]
