from django.contrib import admin
from imagekit.admin import AdminThumbnail

from .models import Documento, ImagenDocumento, TipoDocumento


# Register your models here.

class ImagenDocumentoInline(admin.TabularInline):
    model = ImagenDocumento
    fields = ('admin_thumbnail', 'imagen')
    readonly_fields = ['admin_thumbnail']
    admin_thumbnail = AdminThumbnail(image_field='imagen_thumbnail')
    extra = 0


class DocumentoAdmin(admin.ModelAdmin):
    list_select_related = (
        'tipo',
        'cliente',
    )

    list_filter = (
        'tipo__nomenclatura',
    )

    search_fields = [
        'nro',
        'tipo__nombre',
        'tipo__nomenclatura',
        'cliente__nombre',
        'cliente__nit',
    ]

    raw_id_fields = ('cliente',)

    list_display = ('get_tipo_nomenclatura', 'nro', 'tipo', 'get_cliente_nombre')
    inlines = [
        ImagenDocumentoInline,
    ]

    ordering = ('tipo__nombre','nro',)

    def get_tipo_nomenclatura(self, obj):
        return obj.tipo.nomenclatura
    get_tipo_nomenclatura.short_description = 'Tipo'

    def get_cliente_nombre(self, obj):
        return obj.cliente.nombre
    get_cliente_nombre.short_description = 'Cliente'


admin.site.register(Documento, DocumentoAdmin)
admin.site.register(TipoDocumento)
