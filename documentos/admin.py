from django.contrib import admin
from imagekit.admin import AdminThumbnail

from .models import Documento, ImagenDocumento, TipoDocumento, Transaccion


# Register your models here.

class ImagenDocumentoInline(admin.TabularInline):
    model = ImagenDocumento
    fields = ('admin_thumbnail', 'imagen')
    readonly_fields = ['admin_thumbnail']
    admin_thumbnail = AdminThumbnail(image_field='imagen_thumbnail')
    extra = 0


class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'transaccion')
    inlines = [
        ImagenDocumentoInline,
    ]


admin.site.register(Documento, DocumentoAdmin)
admin.site.register(TipoDocumento)
admin.site.register(Transaccion)
