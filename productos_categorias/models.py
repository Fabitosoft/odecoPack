from django.db import models


# Create your models here.
# region Categorias Producto
class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    nomenclatura = models.CharField(max_length=3, unique=True)

    class Meta:
        verbose_name_plural = "3. Categorías 1"
        verbose_name = "3. Categoría 1"

    def __str__(self):
        return self.nombre


# endregion

# region Categorias Dos
class CategoriaDos(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    nomenclatura = models.CharField(max_length=4, unique=True)

    class Meta:
        verbose_name_plural = "2. Categorías 2"
        verbose_name = "2. Categoría 2"

    def __str__(self):
        return self.nombre


# endregion

# region Categoria Dos por Categoria
class CategoriaDosCategoria(models.Model):
    categoria_uno = models.ForeignKey(CategoriaProducto, related_name='mis_categorias_dos',
                                      on_delete=models.PROTECT, verbose_name='categoría uno')
    categoria_dos = models.ForeignKey(CategoriaDos, related_name='mis_categorias_uno',
                                      on_delete=models.PROTECT, verbose_name='categoría dos')

    class Meta:
        verbose_name_plural = "5. Categorías 2 Productos"
        verbose_name = "5. Categoría 2 Producto"
        unique_together = ["categoria_uno", "categoria_dos"]

    def __str__(self):
        return '%s - %s' %(self.categoria_uno.nombre,self.categoria_dos.nombre)
# endregion

# region Tipos
class TipoProducto(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    nomenclatura = models.CharField(max_length=4, unique=True)

    class Meta:
        verbose_name_plural = "1. Tipo Producto"
        verbose_name = "1. Tipos Productos"

    def __str__(self):
        return self.nombre


# endregion

# region Tipos por Categoria
class TipoProductoCategoría(models.Model):
    categoria_uno = models.ForeignKey(CategoriaProducto, related_name='mis_tipo',
                                      on_delete=models.PROTECT, verbose_name='categorías uno')
    tipo = models.ForeignKey(TipoProducto, on_delete=models.PROTECT, verbose_name='tipo', related_name='mis_categorias')

    class Meta:
        verbose_name_plural = "3. Tipo por Categoria"
        verbose_name = "3. Tipos por Categoria"
        unique_together = ["categoria_uno", "tipo"]

    def __str__(self):
        return '%s - %s' % (self.categoria_uno.nombre, self.tipo.nombre)


# endregion

# region Nombre Estandar
class ProductoNombreConfiguracion(models.Model):
    categoria = models.OneToOneField(CategoriaProducto, on_delete=models.CASCADE, verbose_name='categoría',
                                     related_name='mi_configuracion_producto_nombre_estandar', unique=True)
    con_categoría_uno = models.BooleanField(default=False)
    con_categoría_dos = models.BooleanField(default=False)
    con_serie = models.BooleanField(default=False)
    con_fabricante = models.BooleanField(default=False)
    con_tipo = models.BooleanField(default=False)
    con_material = models.BooleanField(default=False)
    con_color = models.BooleanField(default=False)
    con_ancho = models.BooleanField(default=False)
    con_alto = models.BooleanField(default=False)
    con_longitud = models.BooleanField(default=False)
    con_diametro = models.BooleanField(default=False)

    def __str__(self):
        return self.categoria.nombre

    class Meta:
        verbose_name_plural = 'Configuración Nombres Automáticos'
        verbose_name_plural = 'Configuración Nombre Automático'

# endregion
