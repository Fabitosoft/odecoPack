from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import CreateView, UpdateView

from .models import ContactoEmpresa
from .forms import ContactoEmpresaForm
from biable.models import Cliente


# Create your views here.

class ContactosEmpresaCreateView(CreateView):
    model = ContactoEmpresa
    template_name = 'biable/contacto_empresa_create.html'
    form_class = ContactoEmpresaForm
    cliente = None

    def get_context_data(self, **kwargs):
        nit = self.kwargs.get('nit')
        self.cliente = get_object_or_404(Cliente, nit=nit)
        context = super().get_context_data(**kwargs)
        context['cliente_nombre'] = self.cliente.nombre
        return context

    def get_form(self, form_class=None):
        nit = self.kwargs.get('nit')
        self.cliente = get_object_or_404(Cliente, nit=nit)
        form = super().get_form(form_class)
        form.fields['sucursal'].queryset = self.cliente.mis_sucursales
        return form

class ContactosEmpresaUpdateView(UpdateView):
    model = ContactoEmpresa
    template_name = 'biable/contacto_empresa_update.html'
    form_class = ContactoEmpresaForm
    cliente = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cliente_nombre'] = self.object.sucursal.cliente.nombre
        return context

    def get_form(self, form_class=None):
        nit = self.kwargs.get('nit')
        self.cliente = self.object.sucursal.cliente
        form = super().get_form(form_class)
        form.fields['sucursal'].queryset = self.cliente.mis_sucursales
        return form