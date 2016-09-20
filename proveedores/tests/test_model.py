from django.db import IntegrityError
from django.test import TestCase

from productos.models import UnidadMedida, Producto
from proveedores.models import Moneda, Proveedor, ListaPrecio

class MonedaTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.moneda = Moneda(nombre="USD")
        cls.moneda2 = Moneda(nombre="USD")

    def test_string_representation(self):
        self.assertEqual(str(self.moneda), self.moneda.nombre)

    def test_verbose_name_plural(self):
        self.assertEqual(str(Moneda._meta.verbose_name_plural), "monedas")

    def test_uniqueness_nombre(self):
        self.moneda.save()
        with self.assertRaises(IntegrityError):
            self.moneda2.save()

class ProveedorTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.moneda = Moneda(nombre="USD")
        cls.moneda.save()
        cls.proveedor = Proveedor(nombre="EUROBELT", moneda=cls.moneda)
        cls.proveedor2 = Proveedor(nombre="EUROBELT", moneda=cls.moneda)

    def test_string_representation(self):
        self.assertEqual(str(self.proveedor), self.proveedor.nombre)

    def test_verbose_name_plural(self):
        self.assertEqual(str(Proveedor._meta.verbose_name_plural), "proveedores")

    def test_uniqueness_nombre(self):
        self.proveedor.save()
        with self.assertRaises(IntegrityError):
            self.proveedor2.save()

class ListaPreciosTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.moneda = Moneda(nombre="USD")
        cls.moneda.save()
        cls.proveedor = Proveedor(nombre="EUROBELT", moneda=cls.moneda)
        cls.proveedor.save()

        cls.unidad = UnidadMedida(nombre="metro")
        cls.unidad.save()

        cls.producto = Producto(
            id_cguno=1,
            referencia='referencia',
            descripcion_estandar='descripcion',
            descripcion_comercial='descripcion2',
            unidad_medida=cls.unidad
        )
        cls.producto.save()

        cls.lista_precios = ListaPrecio(
            proveedor=cls.proveedor,
            producto=cls.producto,
            cantidad_minima=1,
            valor=1
        )
        cls.lista_precios2 = ListaPrecio(
            proveedor=cls.proveedor,
            producto=cls.producto,
            cantidad_minima=1,
            valor=1
        )

    def test_string_representation(self):
        self.assertEqual(str(self.lista_precios),
                         "%s %s %s"%(self.lista_precios.proveedor,
                                     self.lista_precios.producto.referencia,
                                     self.lista_precios.cantidad_minima))

    def test_verbose_name_plural(self):
        self.assertEqual(str(ListaPrecio._meta.verbose_name_plural), "listas de precios")

    def test_uniqueness_together(self):
        self.lista_precios.save()
        with self.assertRaises(IntegrityError):
            self.lista_precios2.save()