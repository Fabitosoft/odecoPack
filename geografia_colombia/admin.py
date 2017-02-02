from django.contrib import admin

from import_export.admin import ImportExportModelAdmin

from .models import Departamento, Ciudad, Pais
# Register your models here.

class DepartamentoAdmin(ImportExportModelAdmin):
    pass

class CiudadAdmin(ImportExportModelAdmin):
    list_select_related = ('departamento',)
    list_display = ('nombre','departamento')
    list_filter = ('departamento','departamento__pais')
    search_fields = ('nombre','departamento__nombre')


admin.site.register(Departamento,DepartamentoAdmin)
admin.site.register(Pais)
admin.site.register(Ciudad,CiudadAdmin)