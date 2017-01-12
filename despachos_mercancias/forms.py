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
        )
    )
    class Meta:
        model = EnvioTransportadoraTCC
        fields = ('fecha_entrega', 'rr', 'estado', 'observacion')

    def __init__(self, *args, **kwargs):
        super(EnvioTccForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-envioTccForm'
        self.helper.form_method = "post"

        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            Div(
                Div(
                    Field('fecha_entrega'),
                    Field('estado'),
                ),
                Div(
                    Field('rr'),
                ),
                Div(
                    Field('observacion')
                )
            ),
            FormActions(
                Submit('guardar', 'Guardar')
            )
        )
        self.helper.all().wrap(Field, css_class="form-control")
        # self.helper.filter_by_widget(forms.CharField).wrap(Field, css_class="form-control")
