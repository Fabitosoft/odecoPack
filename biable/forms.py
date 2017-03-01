from django import forms
from crispy_forms.bootstrap import FieldWithButtons, FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, HTML, Div, Field
from django.urls import reverse

from empresas.models import Industria
from .models import Cliente, SeguimientoCliente
from contactos.models import ContactoEmpresa


class ClienteProductoBusquedaForm(forms.Form):
    buscar = forms.CharField(max_length=100, required=False, label="Referencia")

    def __init__(self, *args, **kwargs):
        super(ClienteProductoBusquedaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-busqueda'
        self.helper.form_method = "GET"
        self.helper.form_action = ""

        self.helper.layout = Layout(
            Div(
                FieldWithButtons('buscar', Submit('accion', 'Buscar')),
                css_class="col-sm-5"
            )
        )


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
    industria = forms.ModelChoiceField(queryset=Industria.objects.all().order_by('nombre'), required=False)

    class Meta:
        model = Cliente
        fields = [
            'potencial_compra',
            'cerro',
            'canal',
            'competencia',
            'industria',
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


class CrearSeguimientoClienteForm(forms.ModelForm):
    cliente = forms.IntegerField()
    contacto = forms.ModelChoiceField(queryset=None)
    fecha_seguimiento = forms.DateTimeField(
        widget=forms.TextInput(
            attrs={'type': 'date'}
        )
    )
    hora_inicial = forms.TimeField(
        widget=forms.TextInput(
            attrs={'type': 'time', 'min': "07:00", 'max': "18:00"}
        )
    )
    hora_final = forms.TimeField(
        widget=forms.TextInput(
            attrs={'type': 'time', 'min': "07:00", 'max': "18:00"}
        ), required=False
    )

    class Meta:
        model = SeguimientoCliente
        fields = [
            'tipo',
            'fecha_seguimiento',
            'descripcion',
            'asunto',
            'hora_inicial',
            'hora_final',
        ]

    def __init__(self, *args, **kwargs):
        super(CrearSeguimientoClienteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-seguimiento_form'
        self.helper.form_method = "POST"
        self.fields['contacto'].queryset = ContactoEmpresa.objects.filter(cliente_id=self.initial.get('cliente'))

        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            HTML("<h2>Crear Seguimiento Cliente</h2>"),
            Div(
                Div(
                    Div(
                        Field('cliente'),
                    ),
                    Div(
                        Field('asunto'),
                    ),
                    Div(
                        Field('contacto'),
                    ),
                    Div(
                        Field('tipo'),
                        Field('fecha_seguimiento'),
                    ),
                    Div(
                        Field('hora_inicial'),
                        Field('hora_final'),
                    ),
                    Div(
                        Field('descripcion'),
                    )
                ),
                HTML("<hr/>"),
                FormActions(
                    Submit('guardar_seguimiento', 'Guardar'),
                )
            )
        )
