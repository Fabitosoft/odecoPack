from django.db import IntegrityError
from django.test import TestCase
from productos.models import Producto, UnidadMedida
from django.utils.translation import ugettext_lazy as _

class ProductoTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.unidad = UnidadMedida(nombre="metro")
        cls.unidad.save()
        cls.producto=Producto(
            id_cguno=1,
            referencia='referencia',
            descripcion_estandar='descripcion',
            descripcion_comercial='descripcion2',
            unidad_medida=cls.unidad
        )
        cls.producto2=Producto(
            id_cguno=1,
            referencia='referencia',
            descripcion_estandar='descripcion',
            descripcion_comercial='descripcion2',
            unidad_medida=cls.unidad
        )

    def test_string_representation(self):
        self.assertEqual(str(self.producto), self.producto.descripcion_estandar)

    def test_verbose_name_plural(self):
        self.assertEqual(str(Producto._meta.verbose_name_plural), "productos")

    def test_uniqueness_referencia(self):
        self.producto.save()
        with self.assertRaises(IntegrityError):
            self.producto2.save()


class UnidadMedidaTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.unidad = UnidadMedida(nombre="metro")
        cls.unidad2 = UnidadMedida(nombre="metro")

    def test_string_representation(self):
        self.assertEqual(str(self.unidad), self.unidad.nombre)

    def test_verbose_name_plural(self):
        self.assertEqual(str(UnidadMedida._meta.verbose_name_plural), "unidades de medida")

    def test_uniqueness_nombre(self):
        self.unidad.save()
        with self.assertRaises(IntegrityError):
            self.unidad2.save()