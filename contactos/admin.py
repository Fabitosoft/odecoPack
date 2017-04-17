from django.contrib import admin

from .models import ContactoEmpresa


# Register your models here.
class ContactoEmpresaAdmin(admin.ModelAdmin):
    list_select_related = ('sucursal', 'creado_por', 'creado_por')
    raw_id_fields = ('sucursal','cliente')
    list_display = (
        'nombres',
        'cliente',
        'subempresa',
        'apellidos',
        'correo_electronico',
        'correo_electronico_alternativo',
        'nro_telefonico',
        'nro_telefonico_alternativo',
        'sucursal',
        'creado_por'
    )
    search_fields = (
        'nombres',
        'apellidos',
        'cliente__nombre',
        'correo_electronico',
        'correo_electronico_alternativo'
    )


admin.site.register(ContactoEmpresa, ContactoEmpresaAdmin)
