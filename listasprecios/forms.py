from crispy_forms.bootstrap import FieldWithButtons
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, Field
from django import forms

from listasprecios.models import FormaPago


class ProductoBusqueda(forms.Form):
    buscar = forms.CharField(max_length=100, required=False, label="Referencia")
    tipo = forms.ModelChoiceField(queryset=FormaPago.objects.all().order_by("canal"), label="Forma de Pago")

    def __init__(self, *args, **kwargs):
        super(ProductoBusqueda, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-busqueda'
        self.helper.form_method = "GET"
        self.helper.form_action = ""

        self.helper.layout = Layout(
            Div(
                Field('tipo'),
                css_class="col-sm-3"
            ),
            Div(
                FieldWithButtons('buscar', Submit('accion', 'Buscar')),
                css_class="col-sm-5"
            )
        )
