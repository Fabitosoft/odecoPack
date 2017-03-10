from crispy_forms.bootstrap import StrictButton, PrependedText, FormActions, FieldWithButtons
from crispy_forms.layout import Submit, Layout, Div, Field, Button, HTML
from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.urls import reverse

from crispy_forms.helper import FormHelper
from dal import autocomplete

from .models import (
    Cotizacion,
    RemisionCotizacion,
    TareaCotizacion,
    ItemCotizacion,
    ComentarioCotizacion,
    ImagenCotizacion)

from contactos.models import ContactoEmpresa
from geografia_colombia.models import Ciudad
from biable.models import Cliente, VendedorBiable


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


class CambiarResponsableCotizacionForm(ModelForm):
    usuario = forms.ModelChoiceField(
        queryset=User.objects.filter(
            user_extendido__colaborador__mi_vendedor_biable__activo=True,
        )
    )

    class Meta:
        model = Cotizacion
        fields = ['usuario']

    def __init__(self, *args, **kwargs):
        super(CambiarResponsableCotizacionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-busqueda'
        self.helper.form_method = "post"

        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            Button('cancelar', 'Cambiar Responsable', data_toggle="modal", data_target="#myModal",
                   css_class="btn btn-primary"),
            Div(
                Div(
                    Div(
                        Div(
                            Button('cancelar', 'x', data_dismiss="modal", aria_label="Close", css_class="close"),
                            HTML('<h4 class="modal-title" id="myModalLabel">Cambiar Responsable</h4>'),
                            css_class="modal-header"
                        ),
                        Div(
                            Field('id'),
                            Field('usuario'),
                            css_class="modal-body"
                        ),
                        Div(
                            Submit('asignar_vendedor', 'Asignar', css_class="btn btn-primary"),
                            Button('cancelar', 'Cancelar', data_dismiss="modal", css_class="btn btn-default"),
                            css_class="modal-footer"
                        ), css_class="modal-content"
                    ),
                    role="document",
                    css_class="modal-dialog"
                ),
                css_class="modal fade",
                id="myModal",
                tabindex="-1",
                role="dialog",
                aria_labelledby="myModalLabel"
            )
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


class ImagenCotizacionForm(ModelForm):
    cotizacion_id = forms.IntegerField(widget=forms.HiddenInput)

    class Meta:
        model = ImagenCotizacion
        fields = [
            'imagen',
        ]

    def __init__(self, *args, **kwargs):
        super(ImagenCotizacionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-otro-item'
        self.helper.form_method = "POST"
        self.helper.form_action = reverse('cotizaciones:add_imagen_cotizacion')
        self.cotizacion_id = self.initial.get('cotizacion_id', None)

        # self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            HTML('<h3>Adjuntar Imagen</h3>'),
            Field('cotizacion_id'),
            Div(
                Div(
                    Field('imagen'),
                    css_class='col-md-4'
                ),
            ),
            Submit('add_otro', 'Adicionar'),
        )


class CotizacionForm(ModelForm):
    email = forms.EmailField(label="Correo Electrónico", required=False)
    nro_contacto = forms.CharField(label="Número de Contacto", required=False)
    nombres_contacto = forms.CharField(label="Nombres", required=False)
    apellidos_contacto = forms.CharField(label="Apellidos", required=False)
    contacto_nuevo = forms.BooleanField(label="Contacto nuevo", required=False)
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
    contacto = forms.ModelChoiceField(
        queryset=ContactoEmpresa.objects.all(),
        widget=autocomplete.ModelSelect2(url='contactos:contactos-autocomplete', forward=['cliente_biable']),
        required=False,
        label='Contacto'
    )

    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def clean(self):
        cleaned_data = super(CotizacionForm, self).clean()
        razon_social = cleaned_data.get("razon_social")
        cliente_biable = cleaned_data.get("cliente_biable")
        ciudad_despacho = cleaned_data.get("ciudad_despacho")
        ciudad = cleaned_data.get("ciudad")

        contacto = cleaned_data.get("contacto")
        email = cleaned_data.get("email")
        nombres_contacto = cleaned_data.get("nombres_contacto")
        apellidos_contacto = cleaned_data.get("apellidos_contacto")
        nro_contacto = cleaned_data.get("nro_contacto")

        if (not razon_social and not cliente_biable):
            # Only do something if both fields are valid so far.
            raise forms.ValidationError(
                "Debe tener o razón social o un cliente CGuno."
                " No puede estar vacios los dos campos"
            )

        if (not ciudad_despacho and not ciudad):
            # Only do something if both fields are valid so far.
            raise forms.ValidationError(
                "Debe tener o ciudad alterna o ciudad."
                " No puede estar vacios los dos campos"
            )

        if (not contacto and (not email or not nombres_contacto or not apellidos_contacto or not nro_contacto)):
            # Only do something if both fields are valid so far.
            raise forms.ValidationError(
                "Debe tener información de un contacto."
            )

    class Meta:
        model = Cotizacion
        fields = [
            'id',
            'razon_social',
            'cliente_biable',
            'sucursal_sub_empresa',
            'cliente_nuevo',
            'pais',
            'ciudad',
            'otra_ciudad',
            'ciudad_despacho',
            'nombres_contacto',
            'apellidos_contacto',
            'nro_contacto',
            'email',
            'observaciones',
            'contacto',
            'contacto_nuevo',
        ]

    def __init__(self, *args, **kwargs):
        super(CotizacionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-cotizacionForm'
        self.helper.form_method = "post"
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            Div(
                Field('id'),
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
                Field('contacto'),
            ),
            Div(
                Field('nombres_contacto'),
                Field('apellidos_contacto')
            ),
            Div(
                Field('nro_contacto'),
            ),
            PrependedText('email', '@', placeholder="Correo Electrónico"),
            Div(
                Field('contacto_nuevo'),
            ),
            HTML('<hr/>'),
            Field('observaciones'),
            HTML('<hr/>')

        )
        self.helper.all().wrap(Field, css_class="form-control")
        # self.helper.filter_by_widget(forms.CharField).wrap(Field, css_class="form-control")


class CotizacionCrearForm(CotizacionForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        crear = Div(
            FormActions(
                Submit('formCrea', 'Crear Cotización'),
            )
        )
        self.helper.layout.fields.append(crear)
        self.helper.form_method = "post"
        self.helper.form_action = reverse('cotizaciones:cotizador')


class CotizacionEnviarForm(CotizacionForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        enviar = Div(
            FormActions(
                Submit('formEnvia', 'Enviar Cotización'),
            ),
            HTML('<hr/>'),
            FormActions(
                Submit('formEnvia', 'Descartar', css_class="btn btn-danger")
            ),
        )
        self.helper.layout.fields.append(enviar)
        self.helper.form_method = "post"
        self.helper.form_action = reverse('cotizaciones:cotizador')


class ComentarioCotizacionForm(ModelForm):
    class Meta:
        model = ComentarioCotizacion
        fields = ('comentario', 'cotizacion', 'usuario')

    def __init__(self, *args, **kwargs):
        super(ComentarioCotizacionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-comentario'
        self.helper.form_method = "POST"

        self.helper.layout = Layout(
            Field('cotizacion', type="hidden"),
            Field('usuario', type="hidden"),
            Div(
                Field('comentario'),
                css_class="col-xs-12"
            ),
            Div(
                FormActions(
                    Submit('form_comentar', 'Publicar Comentario'),
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
        self.add_input(Submit("form_remision", "Guardar"))


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
        self.add_input(Submit("form_tareas", "Guardar"))
