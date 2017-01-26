from django.contrib import admin

from .models import (
    TrabajoDiario
)


# Register your models here.
class TrabajoDiaAdmin(admin.ModelAdmin):
    list_display = ['created', 'usuario', 'nro_tareas', 'nro_tareas_atendidas', 'nro_tareas_sin_atender',
                    'porcentaje_atendido']
    readonly_fields = ['nro_tareas', 'nro_tareas_atendidas', 'nro_tareas_sin_atender', 'porcentaje_atendido', 'usuario']


admin.site.register(TrabajoDiario, TrabajoDiaAdmin)
