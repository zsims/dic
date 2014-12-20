import dic
import unittest


class Foo(object):
    pass


class Bar(object):
    def __init__(self, foo: Foo):
        self.foo = foo


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


class Row(object):
    def __init__(self, part: Part, name, description='No description'):
        self.name = name
        self.description = description
        self.part = part


class Table(object):
    def __init__(self, row_factory: dic.rel.Factory(Row)):
        self.data = []
        self.row_factory = row_factory

    def add_row(self, name):
        self.data.append(self.row_factory(name=name))

    def add_row_with_description(self, name, description):
        self.data.append(self.row_factory(name=name, description=description))


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

    def test_factory_can_provide_arguments(self):
        # Arrange
        self.builder.register_class(Row)
        self.builder.register_class(Table)
        self.builder.register_class(Part)
        container = self.builder.build()
        table = container.resolve(Table)

        # Act
        table.add_row('First row')
        table.add_row_with_description('Second row', 'With description')

        # Assert

        # first row should have a default description as defined on the Row class
        self.assertEqual('First row', table.data[0].name)
        self.assertEqual('No description', table.data[0].description,
                         "Should have the same description as the default Row class")

        self.assertEqual('Second row', table.data[1].name)
        self.assertEqual('With description', table.data[1].description)

        self.assertIsInstance(table.data[0].part, Part)
        self.assertIsInstance(table.data[1].part, Part)

    def test_factory_can_override_arguments(self):
        # Arrange
        self.builder.register_class(Bar)
        container = self.builder.build()
        bar_factory = container.resolve(dic.rel.Factory(Bar))

        # Act
        # custom foo (ignoring annotations)
        # note that Foo is not registered
        bar = bar_factory(foo=42)

        # Assert
        self.assertIsInstance(bar, Bar)

        self.assertEqual(bar.foo, 42)

    def test_factory_can_override_registered_arguments(self):
        # Arrange
        self.builder.register_class(Foo)
        self.builder.register_class(Bar)
        container = self.builder.build()
        bar_factory = container.resolve(dic.rel.Factory(Bar))

        # Act
        default_bar = container.resolve(Bar)

        # custom foo (ignoring annotations)
        special_bar = bar_factory(foo=42)

        # Assert
        self.assertIsInstance(default_bar, Bar)
        self.assertIsInstance(default_bar.foo, Foo)
        self.assertEqual(special_bar.foo, 42)

if __name__ == '__main__':
    unittest.main()
