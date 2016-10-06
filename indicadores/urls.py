from django.conf.urls import url

from .views import Prueba

urlpatterns = [
    url(r'^', Prueba.as_view(), name='lp'),
]
