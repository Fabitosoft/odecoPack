from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Colaborador, ClienteEmpresa, UserExtended


# Register your models here.

class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ('get_colaborador_nombre','numero_contacto','extencion','jefe')
    list_editable = ('jefe','numero_contacto','extencion','jefe')
    readonly_fields = ('get_colaborador_nombre',)

    def get_colaborador_nombre(self,obj):
        return obj.usuario.user.get_full_name()
    get_colaborador_nombre.short_description = 'Colaborador'

admin.site.register(Colaborador, ColaboradorAdmin)


class ClienteEmpresaAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        qs1 = None
        if obj is not None:
            qs1 = UserExtended.objects.filter(
                Q(tipo='E') &
                (
                    Q(cliente_empresa__id=obj.usuario.pk) |
                    Q(cliente_empresa__isnull=True)
                )
            )
            form.base_fields['usuario'].queryset = qs1
        else:
            qs1 = UserExtended.objects.filter(
                Q(tipo='E') &
                (
                    Q(cliente_empresa__isnull=True)
                )
            )
            form.base_fields['usuario'].queryset = qs1

        return form


admin.site.register(ClienteEmpresa, ClienteEmpresaAdmin)


# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class UserExtended_Inline(admin.StackedInline):
    model = UserExtended
    can_delete = False
    verbose_name_plural = 'usuario'


# Register your models here.
# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserExtended_Inline,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
