from django.contrib import admin

# Register your models here.

from .models import Banda, Ensamblado, CostoEnsambladoBlanda


# region BandasAdmin
class EnsambladoInline(admin.TabularInline):
    def get_queryset(self, request):
        qs = super().get_queryset(request).prefetch_related('producto')
        return qs

    model = Ensamblado
    raw_id_fields = ("producto",)
    readonly_fields = ("es_para_ensamblado", "get_costo_producto", "precio_linea", "costo_cop_linea", "rentabilidad")
    # can_delete = False
    extra = 0

    def es_para_ensamblado(self, obj):
        return obj.producto.activo_ensamble

    es_para_ensamblado.boolean = True

    def get_costo_producto(self, obj):
        return obj.producto.costo


        # def formfield_for_foreignkey(self, db_field, request, **kwargs):
        #     print(db_field)
        #     if db_field.name=='producto':
        #         kwargs['queryset'] = Producto.activos.modulos()
        #     return super().formfield_for_foreignkey(db_field, request, **kwargs)


class BandaAdmin(admin.ModelAdmin):
    list_display = (
        "referencia",
        "descripcion_comercial",
        "serie",
        "con_empujador",
        "con_aleta",
        "con_torneado_varilla",
        "fabricante",
        "activo",
        'activo_proyectos',
        'activo_componentes',
        'activo_catalogo',
        "costo_base_total",
        "precio_banda",
        "rentabilidad",
        'costo_mano_obra',
        "precio_total",
    )

    search_fields = [
        'referencia',
        'descripcion_estandar',
        'descripcion_comercial',
        'fabricante__nombre',
        'tipo_por_categoria__tipo__nombre',
    ]

    list_filter = (
        'activo', 'activo_proyectos', 'activo_componentes',
        'activo_catalogo')

    list_editable = (
        "activo",
        'activo_proyectos',
        'activo_componentes',
        'activo_catalogo',
    )
    readonly_fields = (
        "precio_total", "costo_base_total", "rentabilidad", "referencia", "costo_mano_obra", "precio_banda")

    fieldsets = (
        ('Informacion General', {
            'classes': ('form-control',),
            'fields':
                (
                    ('id_cguno', 'referencia'),
                    ('descripcion_estandar', 'descripcion_comercial'),
                    'fabricante'
                )
        }),
        ('General', {
            'classes': ('form-control',),
            'fields':
                (
                    ('serie', 'paso'),
                    ('tipo', 'material', 'color'),
                    ('ancho', 'longitud'),
                    'material_varilla',
                    'total_filas',
                    ('con_torneado_varilla'),
                )
        }),
        ('Activar', {
            'fields':
                (
                    ("activo", 'activo_proyectos', 'activo_componentes', 'activo_catalogo'),
                )
        }),
        ('Empujador', {
            'classes': ('collapse',),
            'fields': (
                'con_empujador',
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
                'con_aleta',
                'aleta_altura',
                'aleta_identacion'
            ),
        }),
        ('Precio y Costo', {
            'fields': (
                'costo_base_total',
                'precio_banda',
                'rentabilidad',
                'costo_mano_obra',
                'precio_total',
            ),
        }),
    )

    inlines = [
        EnsambladoInline,
    ]

    def save_model(self, request, obj, form, change):
        obj.generar_referencia()
        if not change:
            obj.created_by = request.user
        else:
            obj.updated_by = request.user
        obj.save()


# endregion

class EnsambladoAdmin(admin.ModelAdmin):
    list_display = ("get_banda_nombre", "get_modulo", "es_para_ensambado")

    def get_banda_nombre(self, obj):
        return obj.banda.descripcion_estandar

    get_banda_nombre.short_description = "Banda"

    def get_modulo(self, obj):
        return obj.producto.descripcion_estandar

    get_modulo.short_description = "Modulo"

    def es_para_ensambado(self, obj):
        return obj.producto.activo_ensamble

    es_para_ensambado.boolean = True
    es_para_ensambado.short_description = "Es para ensamblaje?"


class CostoEnsambladoBlandaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'aleta', 'empujador', 'torneado', 'porcentaje')
    list_editable = ('porcentaje',)


admin.site.register(Banda, BandaAdmin)
admin.site.register(Ensamblado, EnsambladoAdmin)
admin.site.register(CostoEnsambladoBlanda, CostoEnsambladoBlandaAdmin)
