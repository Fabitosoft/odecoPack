from crispy_forms.bootstrap import StrictButton, PrependedText, FormActions, FieldWithButtons
from crispy_forms.layout import Submit, Layout, Div, Field, Button, HTML
from django import forms
from django.forms import ModelForm

from crispy_forms.helper import FormHelper
from django.urls import reverse

from .models import EnvioTransportadoraTCC


class EnvioTccForm(ModelForm):
    fecha_entrega = forms.DateField(
        widget=forms.TextInput(
            attrs={'type': 'date'}
        ), required=False
    )
    fecha_entrega_boom = forms.DateField(
        widget=forms.TextInput(
            attrs={'type': 'date'}
        ), required=False
    )

    class Meta:
        model = EnvioTransportadoraTCC
        fields = ('fecha_entrega', 'fecha_entrega_boom', 'estado', 'observacion')

    def __init__(self, *args, **kwargs):
        super(EnvioTccForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-envioTccForm'
        self.helper.form_method = "post"

        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            HTML('<h2>Seguimiento</h2>'),
            Div(
                Field('fecha_entrega'),
                Field('estado'),
            ),
        )

        boom = Div(
            HTML('<h2>Seguimiento Boom</h2>'),
            Div(
                Field('fecha_entrega_boom'),
            )
        )
        if not self.instance.nro_tracking_boom:
            boom = Div(
                Div(
                    Field('fecha_entrega_boom'),
                ), style="display:none"
            )

        observacion = Div(
            HTML('<h2>Observaciones</h2>'),
            Div(
                Field('observacion')
            ),
            FormActions(
                Submit('guardar', 'Guardar')
            )
        )

        self.helper.layout.fields.append(boom)

        self.helper.layout.fields.append(observacion)

        self.helper.all().wrap(Field, css_class="form-control")
