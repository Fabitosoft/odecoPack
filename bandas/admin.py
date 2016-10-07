from django.contrib import admin

# Register your models here.
from .models import Caracteristica, ValorCaracteristica, Banda, Ensamblado


class EnsambladoInline(admin.TabularInline):
    model = Ensamblado
    can_delete = False
    extra = 0


class BandaAdmin(admin.ModelAdmin):
    fieldsets = (
        ('General', {
            'classes': ('form-control',),
            'fields':
                (
                    ('descripcion_estandar', 'descripcion_comercial'),
                    'referencia',
                    ('serie', 'material', 'color', 'fabricante',),
                    ('ancho', 'longitud'),
                    ('material_varilla',)
                )
        }),
        ('Empujador', {
            'classes': ('collapse',),
            'fields': (
                'empujador',
                'empujador_tipo',
                ('empujador_altura','empujador_ancho'),
                'empujador_distanciado',
                'empujador_identacion',
                ('empujador_filas_entre','empujador_total_filas'),
                ('aleta', 'aleta_identacion')
            ),
        }),
    )
    # list_display = ('referencia','descripcion_estandar','unidad_medida')
    # search_fields = ['referencia','descripcion_estandar']
    inlines = [
        EnsambladoInline,
    ]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        else:
            obj.updated_by = request.user
        obj.save()

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        qsSerie = ValorCaracteristica.objects.filter(caracteristica__nombre__iexact="serie")
        qsEmpujador = ValorCaracteristica.objects.filter(caracteristica__nombre__iexact="empujador")
        qsMaterial = ValorCaracteristica.objects.filter(caracteristica__nombre__iexact="material")
        qsColor = ValorCaracteristica.objects.filter(caracteristica__nombre__iexact="color")
        qsMaterialVarilla = ValorCaracteristica.objects.filter(caracteristica__nombre__iexact="material varilla")
        qsEmpujadorTipo = ValorCaracteristica.objects.filter(caracteristica__nombre__iexact="empujador tipo")
        form.base_fields['serie'].queryset = qsSerie
        form.base_fields['empujador'].queryset = qsEmpujador
        form.base_fields['material'].queryset = qsMaterial
        form.base_fields['color'].queryset = qsColor
        form.base_fields['material_varilla'].queryset = qsMaterialVarilla
        form.base_fields['empujador_tipo'].queryset = qsEmpujadorTipo

        return form


class ValorCaracteristicaInline(admin.TabularInline):
    model = ValorCaracteristica
    extra = 0

class CaracteristicaAdmin(admin.ModelAdmin):
    inlines = [
        ValorCaracteristicaInline,
    ]

admin.site.register(Caracteristica,CaracteristicaAdmin)
admin.site.register(Banda, BandaAdmin)
admin.site.register(Ensamblado)
