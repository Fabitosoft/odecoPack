from django.contrib import admin

from .models import ContactoEmpresa


# Register your models here.
class ContactoEmpresaAdmin(admin.ModelAdmin):
    list_select_related = ('cliente', 'ciudad', 'creado_por')
    raw_id_fields = ('cliente', 'ciudad')
    list_display = (
        'nombres',
        'apellidos',
        'correo_electronico',
        'correo_electronico_alternativo',
        'nro_telefonico',
        'nro_telefonico_alternativo',
        'cliente',
        'ciudad',
        'ciudad_alternativa',
        'creado_por'
    )

admin.site.register(ContactoEmpresa,ContactoEmpresaAdmin)
