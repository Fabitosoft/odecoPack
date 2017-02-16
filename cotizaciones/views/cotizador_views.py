from decimal import Decimal, InvalidOperation
from django.utils import timezone
from django.db.models import F
from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin

from ..models import ItemCotizacion
from ..mixins import EnviarCotizacionMixin

from bandas.models import Banda
from ..forms import (
    CotizacionForm,
    CotizacionCrearForm,
    CotizacionEnviarForm,
    ItemCotizacionOtrosForm
)

from productos.models import (
    Producto,
    ArticuloCatalogo
)

from listasprecios.forms import ProductoBusqueda
from ..models import FormaPago, Cotizacion


class CotizadorView(FormView):
    template_name = 'cotizaciones/cotizador.html'

    def get_lista_precios(self, context):
        query = self.request.GET.get("buscar")
        if query:
            qs_bandas = Banda.activos.componentes().filter(
                Q(referencia__icontains=query) |
                Q(descripcion_estandar__icontains=query) |
                Q(descripcion_comercial__icontains=query)
            ).distinct()

            qs_componentes = Producto.activos.componentes().select_related("unidad_medida").filter(
                Q(referencia__icontains=query) |
                Q(descripcion_estandar__icontains=query) |
                Q(descripcion_comercial__icontains=query)
            ).distinct().order_by('-modified')

            qs_articulos_catalogo = ArticuloCatalogo.objects.filter(
                Q(activo=True) &
                (
                    Q(referencia__icontains=query) |
                    Q(nombre__icontains=query) |
                    Q(categoria__icontains=query)
                )
            ).distinct()

            context['object_list_componentes'] = qs_componentes
            context['object_list_articulos_catalogo'] = qs_articulos_catalogo
            context['object_list_bandas'] = qs_bandas
            context['tab'] = "LISTA_PRECIOS"

    def get_forma_pago(self, context):
        if self.request.GET.get("tipo"):
            context['formas_pago_porcentaje'] = FormaPago.objects.filter(
                id=self.request.GET.get("tipo")).first().porcentaje
        else:
            if FormaPago.objects.all():
                context['formas_pago_porcentaje'] = FormaPago.objects.first().porcentaje
            else:
                context['formas_pago_porcentaje'] = 0

    def post(self, request, *args, **kwargs):

        print(self.request.POST)
        usuario = self.request.user

        id_a_editar = self.request.POST.get('id_a_editar')
        if id_a_editar:
            Cotizacion.objects.filter(actualmente_cotizador=True, usuario=usuario).update(actualmente_cotizador=False)
            cotizacion_actual = Cotizacion.objects.get(id=id_a_editar)
            cotizacion_actual.en_edicion = True
            cotizacion_actual.actualmente_cotizador = True
            cotizacion_actual.save()

        if self.request.POST.get('nueva_cotizacion'):
            self.form_class = CotizacionCrearForm
            Cotizacion.objects.filter(actualmente_cotizador=True, usuario=usuario).update(
                actualmente_cotizador=False)

        if self.request.POST.get('formCrea'):
            self.form_class = CotizacionCrearForm

        if self.request.POST.get('formEnvia'):
            self.form_class = CotizacionEnviarForm

        #
        # print("inicio vista")
        # print(self.request.POST)
        # crear = self.request.POST.get('crear')
        # descartar = self.request.POST.get('descartar')
        #
        # if crear:
        #     formulario = CotizacionCrearForm(self.request.POST)
        #     if formulario.is_valid():
        #         cotizacion = formulario.instance
        #         cotizacion.usuario = self.request.user
        #         cotizacion.fecha_envio = timezone.now()
        #
        #         if not cotizacion.otra_ciudad:
        #             cotizacion.ciudad = None
        #             cotizacion.pais = None
        #         else:
        #             cotizacion.ciudad_despacho = None
        #
        #         if not cotizacion.cliente_nuevo:
        #             cotizacion.razon_social = None
        #         else:
        #             cotizacion.cliente_biable = None
        #
        #         cotizacion.save()
        #         cotizacion = Cotizacion.objects.get(id=cotizacion.id)
        #         cotizacion.actualmente_cotizador = True
        #         cotizacion.nro_cotizacion = "%s - %s" % ('CB', cotizacion.id)
        #
        #         cotizacion.estado = "INI"
        #         cotizacion.save()
        #     else:
        #         print("entro es invalido")
        #
        # if descartar:
        #     cotizacion = Cotizacion.objects.get(id=self.request.POST.get('id'))
        #     if cotizacion.en_edicion:
        #         cotizacion.en_edicion = False
        #         cotizacion.save()
        #     else:
        #         cotizacion.delete()
        #     return redirect('cotizaciones:cotizador')

        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        usuario = self.request.user

        cotizacion_actual = Cotizacion.objects.filter(actualmente_cotizador=True, usuario=usuario).first()
        if cotizacion_actual:
            self.form_class = CotizacionEnviarForm
        else:
            self.form_class = CotizacionCrearForm

        context = super().get_context_data(**kwargs)
        context["cotizaciones_activas"] = Cotizacion.objects.filter(
            Q(usuario=usuario) &
            (
                Q(estado="INI") |
                Q(en_edicion=True)
            )
        ).order_by('id')
        # nueva_cotizacion = self.request.POST.get('nueva_cotizacion')
        # print(self.request.POST)
        # usuario = self.request.user
        #
        # self.obtener_cotizacion_actual(usuario, context)
        #
        #
        # forma_pago_seleccionada = self.request.GET.get('tipo')
        # context["forma_de_pago"] = forma_pago_seleccionada
        #
        # context['busqueda_producto_form'] = ProductoBusqueda(self.request.GET or None)
        #
        # self.get_lista_precios(context)
        # self.get_forma_pago(context)
        #
        # # cotizacion = self.get_cotizacion_abierta()
        #
        # # if cotizacion:
        # #     context["cotizacion_form"] = CotizacionEnviarForm(instance=cotizacion)
        # #
        # #     if cotizacion.en_edicion:
        # #         context["cotizacion_edit"] = cotizacion.nro_cotizacion
        # #
        # #     context["forma_item_otro"] = ItemCotizacionOtrosForm(initial={'cotizacion_id': cotizacion.id})
        # # else:
        # #     context["cotizacion_form"] = CotizacionCrearForm(self.request.POST or None)
        # if self.request.GET.get("buscar"):
        #     context['tab'] = "LISTA_PRECIOS"
        return context

    def get_success_url(self):
        return redirect('cotizaciones:cotizador')

    def obtener_cotizacion_actual(self, usuario, context):
        id_a_editar = self.request.POST.get('id_a_editar')
        if id_a_editar:
            Cotizacion.objects.filter(actualmente_cotizador=True, usuario=usuario).update(actualmente_cotizador=False)
            cotizacion_actual = Cotizacion.objects.get(id=id_a_editar)
            cotizacion_actual.en_edicion = True
            cotizacion_actual.actualmente_cotizador = True
            cotizacion_actual.save()
        else:
            cotizacion_actual = Cotizacion.objects.filter(actualmente_cotizador=True, usuario=usuario).first()
        if cotizacion_actual:
            context["actual_cotizacion"] = cotizacion_actual
            context['tab'] = "COTIZACION"
            context['cotizacion_form'] = CotizacionEnviarForm(instance=cotizacion_actual)
            context["forma_item_otro"] = ItemCotizacionOtrosForm(initial={'cotizacion_id': cotizacion_actual.id})
        else:
            context['cotizacion_nueva_form'] = CotizacionCrearForm(None)
            context['tab'] = "NUEVA"

        return cotizacion_actual


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
