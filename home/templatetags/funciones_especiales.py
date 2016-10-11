from decimal import Decimal
from django import template
import math

register = template.Library()

@register.simple_tag
def arreglar_centenas_lp(valor):
    return math.ceil((valor/100))*100

@register.simple_tag
def obtener_precio_lp(valor,porcentaje):
    nuevo_valor = Decimal(valor)*Decimal((1 + porcentaje))
    return math.ceil((nuevo_valor/100))*100