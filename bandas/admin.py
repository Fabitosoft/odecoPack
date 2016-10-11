from django.contrib import admin

# Register your models here.

from productos.models import Producto
from .models import Caracteristica, ValorCaracteristica, Banda, Ensamblado


class EnsambladoInline(admin.TabularInline):
    model = Ensamblado
    raw_id_fields = ("producto",)
    readonly_fields = ("es_para_ensamblado","precio_linea")
    # can_delete = False
    extra = 0

    def es_para_ensamblado(self, obj):
        return obj.producto.activo_ensamble
    es_para_ensamblado.boolean = True

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     print(db_field)
    #     if db_field.name=='producto':
    #         kwargs['queryset'] = Producto.activos.modulos()
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)


class BandaAdmin(admin.ModelAdmin):

    list_display = (
        "referencia",
        "descripcion_estandar",
        "serie",
        "con_empujador",
        "con_aleta",
        "fabricante",
        "activo",
        "precio_total"
    )

    list_editable = ("activo",)
    readonly_fields = ("precio_total",)

    fieldsets = (
        ('General', {
            'classes': ('form-control',),
            'fields':
                (
                    ('descripcion_estandar', 'descripcion_comercial'),
                    'referencia',
                    ('serie', 'material', 'color', 'fabricante', 'tipo'),
                    ('ancho', 'longitud', 'total_filas'),
                    'material_varilla',
                    ('con_empujador', 'con_aleta'),
                    'activo'
                )
        }),
        ('Empujador', {
            'classes': ('collapse',),
            'fields': (
                'empujador_tipo',
                ('empujador_altura', 'empujador_ancho'),
                'empujador_distanciado',
                'empujador_identacion',
                ('empujador_filas_entre', 'empujador_total_filas')
            ),
        }),
        ('Aleta', {
            'classes': ('collapse',),
            'fields': (
                'aleta', 'aleta_identacion'
            ),
        }),
        ('Precio', {
            'fields': (
                'precio_total',
            ),
        }),
    )

    # list_display = ('referencia','descripcion_estandar','unidad_medida')
    # search_fields = ['referencia','descripcion_estandar']
    inlines = [
        EnsambladoInline,
    ]

    def save_model(self, request, obj, form, change):
        obj.referencia = (
                             "%s"
                             "%s"
                             "%s"
                             "%s"
                             "%s"
                             "%s"
                         ) % \
                         (
                             "B",
                             obj.serie.nomenclatura,
                             obj.tipo.nomenclatura,
                             obj.material.nomenclatura,
                             obj.color.nomenclatura,
                             obj.longitud
                         )
        if not change:
            obj.created_by = request.user
        else:
            obj.updated_by = request.user
        obj.save()

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        qsSerie = ValorCaracteristica.objects.filter(caracteristica__nombre__iexact="serie")
        qsMaterial = ValorCaracteristica.objects.filter(caracteristica__nombre__iexact="material")
        qsColor = ValorCaracteristica.objects.filter(caracteristica__nombre__iexact="color")
        qsMaterialVarilla = ValorCaracteristica.objects.filter(caracteristica__nombre__iexact="material varilla")
        qsEmpujadorTipo = ValorCaracteristica.objects.filter(caracteristica__nombre__iexact="empujador tipo")
        qsTipoBanda = ValorCaracteristica.objects.filter(caracteristica__nombre__iexact="banda tipo")

        form.base_fields['serie'].queryset = qsSerie
        form.base_fields['material'].queryset = qsMaterial
        form.base_fields['color'].queryset = qsColor
        form.base_fields['material_varilla'].queryset = qsMaterialVarilla
        form.base_fields['empujador_tipo'].queryset = qsEmpujadorTipo
        form.base_fields['tipo'].queryset = qsTipoBanda

        return form


class ValorCaracteristicaInline(admin.TabularInline):
    model = ValorCaracteristica
    extra = 0


class CaracteristicaAdmin(admin.ModelAdmin):
    inlines = [
        ValorCaracteristicaInline,
    ]


class EnsambladoAdmin(admin.ModelAdmin):
    list_display = ("get_banda_nombre","get_modulo","es_para_ensambado")

    def get_banda_nombre(self,obj):
        return obj.banda.descripcion_estandar
    get_banda_nombre.short_description = "Banda"

    def get_modulo(self,obj):
        return obj.producto.descripcion_estandar
    get_modulo.short_description = "Modulo"

    def es_para_ensambado(self, obj):
        return obj.producto.activo_ensamble
    es_para_ensambado.boolean = True
    es_para_ensambado.short_description = "Es para ensamblaje?"

admin.site.register(Caracteristica, CaracteristicaAdmin)
admin.site.register(Banda, BandaAdmin)
admin.site.register(Ensamblado,EnsambladoAdmin)
