from django.contrib import admin

# Register your models here.
from django.contrib.admin import DateFieldListFilter

from .models import Banda, Ensamblado, CostoEnsambladoBlanda


# region BandasAdmin
class EnsambladoInline(admin.TabularInline):
    model = Ensamblado
    raw_id_fields = ("producto",)
    readonly_fields = (
        "es_para_ensamblado", "get_costo_cop", "get_costo_producto", "get_costo_cop_linea", "get_precio_base_linea",
        "get_rentabilidad_linea")
    can_delete = False
    extra = 0

    def es_para_ensamblado(self, obj):
        return obj.producto.activo_ensamble

    es_para_ensamblado.boolean = True

    def get_costo_producto(self, obj):
        return obj.producto.costo

    get_costo_producto.short_description = 'Costo'

    def get_costo_cop(self, obj):
        return obj.producto.get_costo_cop()

    get_costo_cop.short_description = 'Costo Cop'

    def get_costo_cop_linea(self, obj):
        return obj.get_costo_cop_linea()

    get_costo_cop_linea.short_description = 'Costo Cop Linea'

    def get_precio_base_linea(self, obj):
        return obj.get_precio_base_linea()

    get_precio_base_linea.short_description = 'Precio Cop Linea'

    def get_rentabilidad_linea(self, obj):
        return obj.get_rentabilidad_linea()

    get_rentabilidad_linea.short_description = 'Rentabilidad'


class BandaAdmin(admin.ModelAdmin):
    precio_base = 0
    costo_base = 0
    costo_mano_obra = 0

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
        "get_costo_cop",
        "get_precio_base",
        # "rentabilidad",
        'get_costo_mano_obra',
        "get_precio_total",
        'created_by',
        'updated_by',
    )

    def get_costo_cop(self, obj):
        self.costo_base = obj.get_costo_cop()
        return self.costo_base

    get_costo_cop.short_description = 'Costo Cop'

    def get_precio_base(self, obj):
        self.precio_base = obj.get_precio_base()
        return self.precio_base

    get_precio_base.short_description = 'Precio Base'

    def get_costo_mano_obra(self, obj):
        self.costo_mano_obra = obj.get_precio_mano_obra()
        return self.costo_mano_obra

    get_costo_mano_obra.short_description = 'Costo Mano Obra'

    def get_precio_total(self, obj):
        return self.precio_base + self.costo_mano_obra

    get_precio_total.short_description = 'Precio Total'

    def get_rentabilidad(self, obj):
        return self.precio_base - self.costo_base

    get_rentabilidad.short_description = 'Rentabilidad'

    search_fields = [
        'referencia',
        'descripcion_estandar',
        'descripcion_comercial',
        'fabricante__nombre',
        'created_by__username',
        'updated_by__username',
        'created_by__first_name',
        'updated_by__first_name',
        'created_by__last_name',
        'updated_by__last_name',
    ]

    list_select_related = (
        "costo_ensamblado",
    )

    list_filter = (
        'activo', 'activo_proyectos', 'activo_componentes',
        'activo_catalogo', 'serie__nombre',
        ('created', DateFieldListFilter)
    )

    list_editable = (
        "activo",
        'activo_proyectos',
        'activo_componentes',
        'activo_catalogo',
    )
    readonly_fields = (
        "get_costo_cop",
        "get_precio_base",
        'get_costo_mano_obra',
        "get_precio_total",
        "get_rentabilidad",
        "referencia"
    )

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
                "get_costo_cop",
                "get_precio_base",
                "get_rentabilidad",
                'get_costo_mano_obra',
                "get_precio_total",
            ),
        }),
        ('Imagen Ensamblado', {
            'fields': (
                "imagen",
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
