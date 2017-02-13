from django import forms
from crispy_forms.bootstrap import FieldWithButtons
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from django.urls import reverse


class ContactoEmpresaBuscador(forms.Form):
    busqueda = forms.CharField(max_length=120)

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
