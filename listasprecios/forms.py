from django import forms

from listasprecios.models import FormaPago


class ProductoBusqueda(forms.Form):
    buscar = forms.CharField(max_length=100, required=False, label="Referencia")
    tipo=forms.ModelChoiceField(queryset=FormaPago.objects.all(), label="Forma de Pago")