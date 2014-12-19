import dic
import unittest


class Part(object):
    def __init__(self):
        self.data = None


class GuyWhoPutsUpWithLaziness(object):
    def __init__(self, bomb: dic.rel.Lazy(Part)):
        self.lazy_part = bomb

    def do_it(self, data):
        self.lazy_part.value.data = data


class SuperFactory(object):
    def __init__(self, part_factory: dic.rel.Factory(Part)):
        self.part_factory = part_factory

    def make(self, data):
        part = self.part_factory()
        part.data = data
        return part


class FactoryTestCase(unittest.TestCase):
    def setUp(self):
        self.builder = dic.container.ContainerBuilder()

    def test_factory_creates_objects(self):
        # Arrange
        self.builder.register_class(Part)
        self.builder.register_class(SuperFactory)
        container = self.builder.build()
        sf = container.resolve(SuperFactory)

        # Act
        p1 = sf.make(1)
        p2 = sf.make(2)
        p3 = sf.make(3)

        # Assert
        self.assertIsInstance(p1, Part)
        self.assertIsInstance(p2, Part)
        self.assertIsInstance(p3, Part)

        self.assertEqual(p1.data, 1)
        self.assertEqual(p2.data, 2)
        self.assertEqual(p3.data, 3)

    def test_lazy_delays_resolve(self):
        # Arrange
        self.builder.register_class(Part)
        self.builder.register_class(GuyWhoPutsUpWithLaziness)
        container = self.builder.build()
        guy = container.resolve(GuyWhoPutsUpWithLaziness)

        self.assertFalse(guy.lazy_part.has_value)

        # Act
        guy.do_it("data")

        # Assert
        self.assertEqual("data", guy.lazy_part.value.data)

if __name__ == '__main__':
    unittest.main()
