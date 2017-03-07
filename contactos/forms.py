from crispy_forms.bootstrap import FieldWithButtons
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.forms import ModelForm
from django.urls import reverse

from .models import ContactoEmpresa


class ContactoEmpresaCreateForm(ModelForm):
    fecha_cumpleanos = forms.DateField(
        widget=forms.TextInput(
            attrs={'type': 'date'}
        ), required=False
    )

    class Meta:
        model = ContactoEmpresa
        exclude = ['cliente','creado_por']

    def __init__(self, *args, **kwargs):
        super(ContactoEmpresaCreateForm, self).__init__(*args, **kwargs)


class ContactoEmpresaForm(ModelForm):
    fecha_cumpleanos = forms.DateField(
        widget=forms.TextInput(
            attrs={'type': 'date'}
        ), required=False
    )

    class Meta:
        model = ContactoEmpresa
        exclude = ['cliente', 'creado_por']

    def __init__(self, *args, **kwargs):
        super(ContactoEmpresaForm, self).__init__(*args, **kwargs)

class ContactoEmpresaBuscador(forms.Form):
    busqueda = forms.CharField(max_length=120, required=False)

    def __init__(self, *args, **kwargs):
        super(ContactoEmpresaBuscador, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-busqueda'
        self.helper.form_method = "GET"
        self.helper.form_action = reverse('contactos:agenda-contactos')

        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            FieldWithButtons('busqueda', Submit('buscar', 'Buscar'))
        )
