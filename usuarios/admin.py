from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Colaborador, ClienteEmpresa, UserExtended

# Register your models here.

class ColaboradorAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        qs1=None
        if obj is not None:
            qs1 = UserExtended.objects.filter(
                Q(tipo='I') &
                (
                    Q(colaborador__id=obj.usuario.pk) |
                    Q(colaborador__isnull=True)
                )
            )
            form.base_fields['usuario'].queryset = (qs1)
        else:
            qs1 = UserExtended.objects.filter(
                Q(tipo='I') &
                (
                    Q(colaborador__isnull=True)
                )
            )
            form.base_fields['usuario'].queryset = (qs1)

        return form
admin.site.register(Colaborador,ColaboradorAdmin)

class ClienteEmpresaAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        qs1=None
        if obj is not None:
            qs1 = UserExtended.objects.filter(
                Q(tipo='E') &
                (
                    Q(cliente_empresa__id=obj.usuario.pk) |
                    Q(cliente_empresa__isnull=True)
                )
            )
            form.base_fields['usuario'].queryset = (qs1)
        else:
            qs1 = UserExtended.objects.filter(
                Q(tipo='E') &
                (
                    Q(cliente_empresa__isnull=True)
                )
            )
            form.base_fields['usuario'].queryset = (qs1)

        return form
admin.site.register(ClienteEmpresa,ClienteEmpresaAdmin)


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