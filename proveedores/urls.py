from django.conf.urls import url

from .views import ListaPreciosView

urlpatterns = [
    url(r'^', ListaPreciosView.as_view(), name='proveedores-lp'),
]
