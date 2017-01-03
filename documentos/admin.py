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
        'tipo__nomenclatura',
    )

    list_filter = (
        'tipo__nomenclatura',
    )

    search_fields = [
        'nro',
        'tipo',
        'tipo__nomenclatura',
        'cliente__nombre',
        'cliente__nit',
    ]
    list_display = ('get_tipo_nomenclatura', 'nro', 'tipo')
    inlines = [
        ImagenDocumentoInline,
    ]

    def get_tipo_nomenclatura(self, obj):
        return obj.tipo.nomenclatura
    get_tipo_nomenclatura.short_description = 'Tipo'


admin.site.register(Documento, DocumentoAdmin)
admin.site.register(TipoDocumento)
