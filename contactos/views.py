from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import CreateView, UpdateView

from braces.views import SelectRelatedMixin

from .models import ContactoEmpresa
from .forms import ContactoEmpresaForm, ContactoEmpresaCreateForm
from biable.models import Cliente


# Create your views here.

class ContactosEmpresaCreateView(CreateView):
    model = ContactoEmpresa
    template_name = 'biable/clientes/contacto_empresa_create.html'
    form_class = ContactoEmpresaCreateForm
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

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.creado_por = self.request.user
        self.object.cliente = self.cliente
        self.object.save()
        return redirect(self.cliente)


class ContactosEmpresaUpdateView(SelectRelatedMixin, UpdateView):
    model = ContactoEmpresa
    select_related = ['sucursal', 'sucursal__cliente']
    template_name = 'biable/clientes/contacto_empresa_update.html'
    form_class = ContactoEmpresaForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cliente_nombre'] = self.object.cliente.nombre
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['sucursal'].queryset = self.object.cliente.mis_sucursales
        return form

    def form_valid(self, form):
        self.object = form.save()
        return redirect(self.object.cliente)
