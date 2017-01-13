from django.contrib import admin

from import_export.admin import ImportExportModelAdmin

from .models import Departamento, Ciudad
# Register your models here.

class DepartamentoAdmin(ImportExportModelAdmin):
    pass

class CiudadAdmin(ImportExportModelAdmin):
    list_display = ('nombre','departamento')


admin.site.register(Departamento,DepartamentoAdmin)
admin.site.register(Ciudad,CiudadAdmin)