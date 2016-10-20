from django.contrib import admin
from .models import (
    CategoriaProducto,
    ProductoNombreConfiguracion,
    CategoriaDosCategoria,
    TipoProducto,
    TipoProductoCategoría,
    CategoriaDos
)
# Register your models here.
class ProductoNombreConfiguracionInLine(admin.TabularInline):
    model = ProductoNombreConfiguracion

class CategoriaDosProductoInLine(admin.TabularInline):
    model = CategoriaDosCategoria
    extra = 1

class TipoProductoCategoríaInLine(admin.TabularInline):
    model = TipoProductoCategoría
    extra = 1


class CategoriaProductoAdmin(admin.ModelAdmin):
    inlines = [
        ProductoNombreConfiguracionInLine,
        CategoriaDosProductoInLine,
        TipoProductoCategoríaInLine
    ]


admin.site.register(CategoriaProducto, CategoriaProductoAdmin)
admin.site.register(TipoProducto)
admin.site.register(CategoriaDos)