from django import forms
from django.forms import ModelForm

from cotizaciones.models import Cotizacion


class CotizacionForm(ModelForm):
    class Meta:
        model = Cotizacion
        exclude = ['estado','total']