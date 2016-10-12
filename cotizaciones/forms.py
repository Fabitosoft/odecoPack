from crispy_forms.bootstrap import StrictButton, PrependedText, FormActions, FieldWithButtons
from crispy_forms.bootstrap import InlineField
from crispy_forms.layout import Submit, Layout, Div, Field, Button, HTML
from django import forms
from django.forms import ModelForm

from crispy_forms.helper import FormHelper
from django.urls import reverse

from cotizaciones.models import Cotizacion


class BusquedaCotiForm(forms.Form):
    buscado = forms.CharField(max_length=70, required=False)

    def __init__(self, *args, **kwargs):
        super(BusquedaCotiForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-busqueda'
        self.helper.form_method = "GET"
        self.helper.form_action = reverse('cotizaciones:buscar_cotizacion')

        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            FieldWithButtons('buscado', Submit('buscar', 'Buscar'))
        )


class CotizacionForm(ModelForm):
    email = forms.EmailField(label="Correo Electrónico")
    nro_contacto = forms.CharField(label="Número de Contacto")
    nombres_contacto = forms.CharField(label="Nombres")
    apellidos_contacto = forms.CharField(label="Apellidos")
    razon_social = forms.CharField(label="Razón Social")

    class Meta:
        model = Cotizacion
        exclude = ['estado', 'total', 'usuario']

    def __init__(self, *args, **kwargs):
        super(CotizacionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-cotizacionForm'
        self.helper.form_method = "GET"

        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            Div(
                Field('razon_social'),
                Field('nro_contacto')
            ),
            Div(
                Field('pais'),
                Field('ciudad')
            ),
            Div(
                Field('nombres_contacto'),
                Field('apellidos_contacto')
            ),
            PrependedText('email', '@', placeholder="Correo Electrónico"),
            HTML('<hr/>')

        )
        crear = Div(
            FormActions(
                Submit('crear', 'Crear Cotización'),
            )
        )
        enviar = Div(
            FormActions(
                Submit('enviar', 'Enviar Cotización')
            )
        )

        if not self.instance.pk:
            self.helper.layout.fields.append(crear)
        else:
            self.helper.layout.fields.append(enviar)
            self.helper.form_action = reverse('cotizaciones:detalle_cotizacion', kwargs={'pk': self.instance.pk})

        self.helper.all().wrap(Field, css_class="form-control")
        # self.helper.filter_by_widget(forms.CharField).wrap(Field, css_class="form-control")
