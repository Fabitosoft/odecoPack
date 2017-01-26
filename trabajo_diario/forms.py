from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, Field
from django import forms
from django.urls import reverse

from .models import SeguimientoCartera, SeguimientoCotizacion, SeguimientoEnvioTCC


class SeguimientoTareaForm(forms.Form):
    ESTADOS = (
        (0, 'Pendiente'),
        (1, 'Atendida en Proceso'),
        (2, 'Atendida Terminada'),
    )
    observacion = forms.CharField(widget=forms.Textarea, required=False)
    estado = forms.ChoiceField(choices=ESTADOS)
    tarea_id = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super(SeguimientoTareaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-tarea'
        self.helper.form_method = "POST"

        self.helper.layout = Layout(
            Div(
                Field('estado'),
                Field('observacion'),
                css_class="col-xs-12"
            ),
            Div(
                FormActions(
                    Submit('guardar', 'Guardar Cambios'),
                )
            )
        )
