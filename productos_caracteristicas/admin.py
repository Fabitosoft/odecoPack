from django.contrib import admin

from .models import (
    UnidadMedida,
    ColorProducto,
    MaterialProducto,
    SerieProducto,
    FabricanteProducto
)

# Register your models here.
admin.site.register(UnidadMedida)
admin.site.register(ColorProducto)
admin.site.register(MaterialProducto)
admin.site.register(SerieProducto)
admin.site.register(FabricanteProducto)