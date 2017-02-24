from django import forms
from crispy_forms.bootstrap import FieldWithButtons, FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, HTML, Div, Field
from django.urls import reverse

from .models import Cliente


class ContactoEmpresaBuscador(forms.Form):
    busqueda = forms.CharField(max_length=120, required=False)

    def __init__(self, *args, **kwargs):
        super(ContactoEmpresaBuscador, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-busqueda'
        self.helper.form_method = "GET"
        self.helper.form_action = reverse('biable:clientes-lista')

        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            FieldWithButtons('busqueda', Submit('buscar', 'Buscar'))
        )


class ClienteDetailEditForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'potencial_compra',
            'cerro',
            'canal',
            'competencia',
            'industria'
        ]

    def __init__(self, *args, **kwargs):
        super(ClienteDetailEditForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-cliente_form'
        self.helper.form_method = "POST"

        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            HTML("<h2>Actualizar Información Cliente</h2>"),
            Div(
                Div(
                    Div(
                        Field('cerro'),
                    ),
                    Div(
                        Field('competencia'),
                    ),
                    Div(
                        Field('potencial_compra'),
                        Field('canal'),
                        Field('industria'),
                        css_class="col-md-12"
                    ), css_class="row"
                ),
                HTML("<hr/>"),
                FormActions(
                    Submit('guardar', 'Guardar'),
                )
            )
        )
