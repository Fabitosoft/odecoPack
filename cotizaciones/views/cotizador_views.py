from decimal import Decimal, InvalidOperation

from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic import CreateView, UpdateView
from django.views.generic.detail import SingleObjectMixin

from braces.views import SelectRelatedMixin, LoginRequiredMixin

from ..models import ItemCotizacion
from ..mixins import EnviarCotizacionMixin, CotizacionesActualesMixin, ListaPreciosMixin

from ..forms import (
    CotizacionCrearForm,
    CotizacionEnviarForm
)

from productos.models import (
    Producto
)

from ..models import Cotizacion


class CotizadorView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        usuario = self.request.user
        nueva_cotizacion = self.request.GET.get('nueva_cotizacion')
        if nueva_cotizacion:
            Cotizacion.objects.filter(actualmente_cotizador=True, usuario=usuario).update(
                actualmente_cotizador=False)
            cotizacion_cotizador = None
        else:
            cotizacion_cotizador = Cotizacion.objects.only('pk').filter(actualmente_cotizador=True,
                                                                        usuario=usuario).first()

        if cotizacion_cotizador:
            kwargs['pk'] = cotizacion_cotizador.pk
            view = CotizacionUpdateView.as_view()
        else:
            view = CotizacionCreateView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        id_a_editar = self.request.POST.get('id_a_editar')
        if id_a_editar:
            view = CambiarCotizacionActualView.as_view()

        form_enviar_descartar = self.request.POST.get('formEnvia')
        if form_enviar_descartar:
            kwargs['pk'] = self.request.POST.get('id')
            if form_enviar_descartar == 'Enviar Cotización':
                view = CotizacionUpdateView.as_view()
            else:
                view = DescartarCotizacionActualView.as_view()

        form_crear = self.request.POST.get('formCrea')
        if form_crear:
            view = CotizacionCreateView.as_view()
        return view(request, *args, **kwargs)


class CotizacionUpdateView(
    SelectRelatedMixin,
    EnviarCotizacionMixin,
    ListaPreciosMixin,
    CotizacionesActualesMixin,
    UpdateView
):
    template_name = 'cotizaciones/cotizador/cotizador.html'
    model = Cotizacion
    form_class = CotizacionEnviarForm
    context_object_name = 'cotizacion_actual'
    select_related = ['cliente_biable', ]

    def form_valid(self, form):
        if not form.instance.items.exists():
            mensaje = "No se puede enviar una cotización sin items"
            messages.add_message(self.request, messages.ERROR, mensaje)
            return redirect('cotizaciones:cotizador')
        if form.instance.estado == "INI":
            form.instance.estado = "ENV"
        form.instance.actualmente_cotizador = False
        if form.instance.en_edicion:
            form.instance.version += 1
        form.instance.en_edicion = False
        form.instance.fecha_envio = timezone.now()
        form.save()
        self.enviar_cotizacion(self.object, self.request.user)

        if self.object.usuario != self.request.user:
            return redirect('cotizaciones:listar_cotizaciones')
        return super().form_valid(form)


class CotizacionCreateView(ListaPreciosMixin, CotizacionesActualesMixin, CreateView):
    model = Cotizacion
    form_class = CotizacionCrearForm
    template_name = 'cotizaciones/cotizador/cotizador.html'

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        form.instance.creado_por = self.request.user
        form.instance.actualmente_cotizador = True
        form.instance.estado = "INI"
        form.instance.en_edicion = False
        cotizacion = form.save()
        cotizacion.nro_cotizacion = "%s - %s" % ('CB', cotizacion.id)
        cotizacion.save()
        return redirect('cotizaciones:cotizador')


class CambiarCotizacionActualView(View):
    def post(self, request, *args, **kwargs):
        usuario = self.request.user
        id_a_editar = self.request.POST.get('id_a_editar')
        Cotizacion.objects.filter(actualmente_cotizador=True, usuario=usuario).update(actualmente_cotizador=False)
        cotizacion_actual = Cotizacion.objects.get(id=id_a_editar)
        cotizacion_actual.actualmente_cotizador = True
        cotizacion_actual.save()
        return redirect('cotizaciones:cotizador')


class DescartarCotizacionActualView(View):
    def post(self, request, *args, **kwargs):
        cotizacion = Cotizacion.objects.get(id=self.request.POST.get('id'))
        if cotizacion.en_edicion:
            cotizacion.en_edicion = False
            cotizacion.actualmente_cotizador = False
            cotizacion.save()
        else:
            cotizacion.delete()
        return redirect('cotizaciones:cotizador')


class AddItemCantidad(SingleObjectMixin, View):
    model = ItemCotizacion

    def get(self, request, *args, **kwargs):
        delete = False
        error_cantidad = False
        actual_item_error = ""
        item_id = request.GET.get("item")
        item = ItemCotizacion.objects.get(id=item_id)
        try:
            qty = Decimal(request.GET.get("qty"))
            if qty <= 0:
                delete = True
                item.delete()
            else:
                item.cantidad = qty
                descuento = (item.precio * qty) * (item.porcentaje_descuento / 100)
                item.descuento = descuento
                item.total = (item.precio * qty) - descuento
                item.save()
            total_linea = round(item.total, 2)
            total_cotizacion = round(item.cotizacion.total, 2)
        except InvalidOperation as e:
            error_cantidad = True
            actual_item_error = item.get_nombre_item()
            total_linea = "ERROR CANTIDAD"
            total_cotizacion = "ERROR CANTIDAD"

        data = {
            "error_cantidad": error_cantidad,
            "actual_item_error": actual_item_error,
            "deleted": delete,
            "total_line": total_linea,
            "descuento": round(item.descuento, 2),
            "descuento_total": round(item.cotizacion.descuento, 2),
            "total_cotizacion": total_cotizacion
        }

        return JsonResponse(data)


class CambiarDiaEntregaView(SingleObjectMixin, View):
    model = ItemCotizacion

    def get(self, request, *args, **kwargs):
        item_id = request.GET.get("item")
        item = ItemCotizacion.objects.get(id=item_id)
        error_cantidad = False
        actual_item_error = ""
        try:
            dias = Decimal(request.GET.get("dias"))
            item.dias_entrega = dias
            item.save()
        except InvalidOperation as e:
            error_cantidad = True
            actual_item_error = item.get_nombre_item()

        data = {
            "dias": item.dias_entrega,
            "error_cantidad": error_cantidad,
            "actual_item_error": actual_item_error
        }
        return JsonResponse(data)


class CambiarPorcentajeDescuentoView(SingleObjectMixin, View):
    model = ItemCotizacion

    def get(self, request, *args, **kwargs):
        item_id = request.GET.get("item")
        item = ItemCotizacion.objects.get(id=item_id)
        error_porcentaje = False
        error_mensaje = ""

        try:
            desc = Decimal(request.GET.get("desc"))
            if desc >= 0:
                item.porcentaje_descuento = desc
                descuento = (item.precio * item.cantidad) * (desc / 100)
                item.descuento = descuento
                item.total = (item.precio * item.cantidad) - descuento
                item.save()
                total_linea = round(item.total, 2)
                descuento_linea = round(item.descuento, 2)
                descuento_cotizacion = round(item.cotizacion.descuento, 2)
                total_cotizacion = round(item.cotizacion.total, 2)
            else:
                error_porcentaje = True
                error_mensaje = "Error en el porcentaje aplicado a %s, debe de ser un número igual o mayor a 1" % (
                    item.get_nombre_item())
                total_linea = "Error en % descuento"
                descuento_linea = "Error en % descuento"
                descuento_cotizacion = "Error en % descuento"
                total_cotizacion = "Error en % descuento"
        except InvalidOperation as e:
            error_porcentaje = True
            error_mensaje = "Error en el porcentaje aplicado a %s, debe ser un número valido" % (item.get_nombre_item())
            total_linea = "Error en % descuento"
            descuento_linea = "Error en % descuento"
            descuento_cotizacion = "Error en % descuento"
            total_cotizacion = "Error en % descuento"

        data = {
            "error_porcentaje": error_porcentaje,
            "error_mensaje": error_mensaje,
            "desc": round(item.porcentaje_descuento, 2),
            "total_line": total_linea,
            "descuento": descuento_linea,
            "descuento_total": descuento_cotizacion,
            "total_cotizacion": total_cotizacion
        }
        return JsonResponse(data)


class AddItem(SingleObjectMixin, View):
    model = ItemCotizacion

    def get(self, request, *args, **kwargs):
        coti_id = kwargs["cot_id"]
        item_id = kwargs["item_id"]
        precio = kwargs["precio"]
        forma_pago_id = kwargs["forma_pago"]
        tipo = int(kwargs["tipo"])
        if tipo == 1:
            item = ItemCotizacion.objects.filter(
                Q(item_id=item_id) &
                Q(cotizacion_id=coti_id)
            ).first()
        elif tipo == 2:
            item = ItemCotizacion.objects.filter(
                Q(articulo_catalogo_id=item_id) &
                Q(cotizacion_id=coti_id)
            ).first()
        else:
            item = ItemCotizacion.objects.filter(
                Q(banda_id=item_id) &
                Q(cotizacion_id=coti_id)
            ).first()

        if not item:
            item = ItemCotizacion()
            if tipo == 1:
                producto = Producto.objects.get(id=item_id)
                item.cantidad = producto.cantidad_empaque
            else:
                item.cantidad = 1

        item.cotizacion_id = coti_id

        if tipo == 1:
            item.item_id = item_id
        elif tipo == 2:
            item.articulo_catalogo_id = item_id
        else:
            item.banda_id = item_id

        item.precio = precio
        item.forma_pago_id = forma_pago_id
        item.total = float(precio) * float(item.cantidad)
        item.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class AddItemOtro(SingleObjectMixin, View):
    model = ItemCotizacion

    def post(self, request, *args, **kwargs):
        coti_id = request.POST.get('cotizacion_id')
        precio = request.POST.get('precio')
        nombre = request.POST.get('p_n_lista_descripcion')
        referencia = request.POST.get('p_n_lista_referencia')
        p_n_lista_unidad_medida = request.POST.get('p_n_lista_unidad_medida')
        item = ItemCotizacion.objects.filter(
            Q(p_n_lista_descripcion=nombre) &
            Q(cotizacion_id=coti_id)
        ).first()
        if not item:
            item = ItemCotizacion()
            item.cantidad = 1
            item.cotizacion_id = coti_id
        item.p_n_lista_descripcion = nombre
        item.p_n_lista_referencia = referencia
        item.p_n_lista_unidad_medida = p_n_lista_unidad_medida
        item.precio = precio
        item.total = precio * item.cantidad
        item.save()

        return redirect('cotizaciones:cotizador')
