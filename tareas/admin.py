from django.contrib import admin

# Register your models here.
from .models import Tarea


class TareaAdmin(admin.ModelAdmin):
    list_display = ('nombre','fecha_inicial','fecha_final','esta_finalizada')

admin.site.register(Tarea, TareaAdmin)
