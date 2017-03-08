from dal import autocomplete
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView

from braces.views import SelectRelatedMixin, LoginRequiredMixin

from .models import ContactoEmpresa
from .forms import ContactoEmpresaForm, ContactoEmpresaCreateForm, ContactoEmpresaBuscador
from biable.models import Cliente, SucursalBiable


# Create your views here.

class ContactosEmpresaCreateView(LoginRequiredMixin, CreateView):
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


class AgendaContactoListView(LoginRequiredMixin, SelectRelatedMixin, ListView):
    model = ContactoEmpresa
    context_object_name = 'contactos_list'
    template_name = 'contactos/contactos_list.html'
    paginate_by = 50
    select_related = ['cliente', 'creado_por', 'cliente__grupo']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_busqueda'] = ContactoEmpresaBuscador(self.request.GET or None)
        return context

    def get_queryset(self):
        q = self.request.GET.get('busqueda')
        usuario = self.request.user
        qs = super().get_queryset()
        if not usuario.is_superuser:
            clientes = SucursalBiable.objects.values_list('cliente_id').filter(
                vendedor_real__colaborador__usuario__user=usuario)
            qs = qs.filter(
                cliente_id__in=clientes
            ).exclude(cliente__nit='')

        if q:
            qs = qs.filter(
                Q(nombres__icontains=q) |
                Q(apellidos__icontains=q) |
                Q(cliente__grupo__nombre__icontains=q) |
                Q(cliente__nit__icontains=q) |
                Q(cliente__nombre__icontains=q)
            )

        qs = qs.distinct().order_by('nombres')
        return qs


class ContactoAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Cliente.objects.none()

        qs = ContactoEmpresa.objects.all()

        cliente_id = self.forwarded.get('cliente_biable', None)

        if cliente_id:
            qs = qs.filter(cliente_id=cliente_id, retirado=False)
            if self.q:
                qs = qs.filter(
                    Q(nombres__icontains=self.q) |
                    Q(cliente__nombre__icontains=self.q) |
                    Q(apellidos__icontains=self.q)
                )
        else:
            qs = qs.none()
        return qs
