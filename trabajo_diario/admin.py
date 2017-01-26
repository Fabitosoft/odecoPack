from django.contrib import admin

from .models import TrabajoDiario, TareaDiaria


# Register your models here.

class TareaDiariaInline(admin.TabularInline):
    model = TareaDiaria
    extra = 0
    readonly_fields = ("tipo","descripcion","estado","observacion")

class TrabajoDiaAdmin(admin.ModelAdmin):
    inlines = [TareaDiariaInline,]
    list_display = ['created','usuario', 'nro_tareas', 'nro_tareas_atendidas', 'nro_tareas_sin_atender',
                    'porcentaje_atendido']
    readonly_fields = ['nro_tareas', 'nro_tareas_atendidas','nro_tareas_sin_atender','porcentaje_atendido','usuario']

admin.site.register(TrabajoDiario, TrabajoDiaAdmin)
