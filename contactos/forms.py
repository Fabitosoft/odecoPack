from django import forms
from django.forms import ModelForm
from .models import ContactoEmpresa



class ContactoEmpresaForm(ModelForm):
    fecha_cumpleanos = forms.DateField(
        widget=forms.TextInput(
            attrs={'type': 'date'}
        ), required=False
    )

    class Meta:
        model = ContactoEmpresa
        exclude = ('creado_por',)

    def __init__(self, *args, **kwargs):
        super(ContactoEmpresaForm, self).__init__(*args, **kwargs)