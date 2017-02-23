from django.contrib import admin

from .models import ContactoEmpresa


# Register your models here.
class ContactoEmpresaAdmin(admin.ModelAdmin):
    list_select_related = ('sucursal', 'creado_por', 'creado_por')
    raw_id_fields = ('sucursal',)
    list_display = (
        'nombres',
        'subempresa',
        'apellidos',
        'correo_electronico',
        'correo_electronico_alternativo',
        'nro_telefonico',
        'nro_telefonico_alternativo',
        'sucursal',
        'creado_por'
    )


admin.site.register(ContactoEmpresa, ContactoEmpresaAdmin)
