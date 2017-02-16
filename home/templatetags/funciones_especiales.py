from decimal import Decimal
from django import template
import math

register = template.Library()


@register.simple_tag
def arreglar_centenas_lp(valor):
    return math.ceil((valor / 100)) * 100


@register.simple_tag
def obtener_precio_lp(valor, porcentaje):
    nuevo_valor = Decimal(valor) * Decimal((1 + (porcentaje / 100)))
    return math.ceil((nuevo_valor / 100)) * 100


@register.simple_tag
def obtener_rentabilidad(costo, precio, *args, **kwargs):
    retorno = precio - costo
    if kwargs['cantidad'] != -1:
        cantidad = kwargs['cantidad']
        precio = cantidad * precio
        costo = cantidad * costo
        retorno = precio - costo
    if kwargs['porcentaje'] == 1:
        retorno = (retorno / precio)
    return retorno


@register.simple_tag
def multiplicar(valor1, valor2):
    return Decimal(valor1) * Decimal(valor2)
