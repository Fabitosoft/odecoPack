from crispy_forms.bootstrap import StrictButton, PrependedText, FormActions, FieldWithButtons
from crispy_forms.layout import Submit, Layout, Div, Field, Button, HTML
from django import forms
from django.forms import ModelForm
from django.urls import reverse

from crispy_forms.helper import FormHelper
from dal import autocomplete

from .models import (
    Cotizacion,
    RemisionCotizacion,
    TareaCotizacion,
    ItemCotizacion,
    ComentarioCotizacion
)
from geografia_colombia.models import Ciudad
from biable.models import Cliente


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


class ItemCotizacionOtrosForm(ModelForm):
    cotizacion_id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ItemCotizacion
        fields = ['precio', 'p_n_lista_descripcion', 'p_n_lista_referencia', 'p_n_lista_unidad_medida']

    def __init__(self, *args, **kwargs):
        super(ItemCotizacionOtrosForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-otro-item'
        self.helper.form_method = "POST"
        self.helper.form_action = reverse('cotizaciones:add_item_otro_cotizacion')

        # self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            Field('cotizacion_id'),
            Field('p_n_lista_descripcion'),
            Div(
                Div(
                    Field('p_n_lista_referencia'),
                    css_class='col-md-4'
                ),
                Div(
                    Field('p_n_lista_unidad_medida'),
                    css_class='col-md-4'
                ),
                Div(
                    Field('precio'),
                    css_class='col-md-4'
                ),
                css_class='row'
            ),
            Submit('add_otro', 'Adicionar'),
        )


class CotizacionForm(ModelForm):
    email = forms.EmailField(label="Correo Electrónico")
    nro_contacto = forms.CharField(label="Número de Contacto")
    nombres_contacto = forms.CharField(label="Nombres")
    apellidos_contacto = forms.CharField(label="Apellidos")
    razon_social = forms.CharField(label="Razón Social", required=False)
    observaciones = forms.Textarea()
    ciudad_despacho = forms.ModelChoiceField(
        queryset=Ciudad.objects.select_related('departamento', 'departamento__pais').all(),
        widget=autocomplete.ModelSelect2(url='geografia:ciudad-autocomplete'),
        required=False
    )
    cliente_biable = forms.ModelChoiceField(
        queryset=Cliente.objects.all(),
        widget=autocomplete.ModelSelect2(url='biable:cliente-autocomplete'),
        required=False,
        label='Cliente CGuno'
    )

    class Meta:
        model = Cotizacion
        exclude = ['estado', 'total', 'usuario']

    def __init__(self, *args, **kwargs):
        super(CotizacionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-cotizacionForm'
        self.helper.form_method = "post"

        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            Div(
                Field('razon_social'),
                Field('cliente_biable'),
            ),
            Div(
                Field('sucursal_sub_empresa'),
            ),
            Div(
                Field('cliente_nuevo')
            ),
            Div(
                Field('pais'),
                Field('ciudad'),
            ),
            Div(
                Field('ciudad_despacho'),
            ),
            Div(
                Field('otra_ciudad')
            ),
            Div(
                Field('nombres_contacto'),
                Field('apellidos_contacto')
            ),
            Div(
                Field('nro_contacto'),
            ),
            PrependedText('email', '@', placeholder="Correo Electrónico"),
            HTML('<hr/>'),
            Field('observaciones'),
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
            self.helper.form_method = "post"
            self.helper.form_action = reverse('cotizaciones:enviar', kwargs={'pk': self.instance.pk})

        self.helper.all().wrap(Field, css_class="form-control")
        # self.helper.filter_by_widget(forms.CharField).wrap(Field, css_class="form-control")


class ComentarioCotizacionForm(ModelForm):
    class Meta:
        model = ComentarioCotizacion
        fields = ('comentario', 'cotizacion',)

    def __init__(self, *args, **kwargs):
        super(ComentarioCotizacionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-comentario'
        self.helper.form_method = "POST"
        self.helper.form_action = reverse('cotizaciones:comentar')

        self.helper.layout = Layout(
            Field('cotizacion', type="hidden"),
            Div(
                Field('comentario'),
                css_class="col-xs-12"
            ),
            Div(
                FormActions(
                    Submit('comentar', 'Publicar Comentario'),
                )
            )
        )


class RemisionCotizacionForm(ModelForm):
    fecha_prometida_entrega = forms.DateField(
        widget=forms.TextInput(
            attrs={'type': 'date'}
        )
    )

    class Meta:
        model = RemisionCotizacion
        fields = ('__all__')


class TareaCotizacionForm(ModelForm):
    fecha_inicial = forms.DateField(
        widget=forms.TextInput(
            attrs={'type': 'date'}
        )
    )
    fecha_final = forms.DateField(
        widget=forms.TextInput(
            attrs={'type': 'date'}
        )
    )

    class Meta:
        model = TareaCotizacion
        fields = ('__all__')


class RemisionCotizacionFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(RemisionCotizacionFormHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.form_class = 'form-inline'

        self.render_required_fields = True
        self.layout = Layout(
            Div(
                Div(
                    Field('tipo_remision'),
                    Field('nro_remision'),
                    Field('fecha_prometida_entrega'),
                ),
                Div(
                    Field('entregado')
                ),
                Div(
                    Field('DELETE')
                ),
                css_class='borde_div'
            ),
            HTML("<br/>")
        )
        self.add_input(Submit("cambiar_remision", "Guardar"))


class TareaCotizacionFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(TareaCotizacionFormHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.form_class = 'form-inline'

        self.render_required_fields = True
        self.layout = Layout(
            Div(
                Div(
                    Field('nombre'),
                    Field('fecha_inicial'),
                    Field('fecha_final'),
                ),
                Div(
                    Field('descripcion', rows="4")
                ),
                Div(
                    Field('esta_finalizada')
                ),
                Div(
                    Field('DELETE')
                ),
                css_class='borde_div'
            ),
            HTML("<br/>")
        )
        self.add_input(Submit("cambiar_tareas", "Guardar"))
