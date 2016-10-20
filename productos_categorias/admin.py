from django.contrib import admin
from .models import (
    CategoriaProducto,
    ProductoNombreConfiguracion
)
# Register your models here.
class ProductoNombreConfiguracionInLine(admin.TabularInline):
    model = ProductoNombreConfiguracion


class CategoriaProductoAdmin(admin.ModelAdmin):
    inlines = [ProductoNombreConfiguracionInLine, ]


admin.site.register(CategoriaProducto, CategoriaProductoAdmin)