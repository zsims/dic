import dic
import unittest


class Standalone(object):
    pass


class SimpleComponent(object):
    def __init__(self, s: Standalone):
        self.standalone = s


class ContainerBuilderTestCase(unittest.TestCase):
    def setUp(self):
        self.builder = dic.container.ContainerBuilder()

    def test_build_creates_empty_container(self):
        # Arrange
        # Act
        self.builder.build()

        # Assert
        # No explosions

    def test_register_class_no_deps(self):
        # Arrange
        self.builder.register_class(Standalone)

        # Act
        container = self.builder.build()

        # Assert
        self.assertEqual(len(container.registry_map), 1)

    def test_register_class_simple_deps(self):
        # Arrange
        self.builder.register_class(SimpleComponent)

        # Act
        container = self.builder.build()

        # Assert
        self.assertEqual(len(container.registry_map), 1)


class ContainerTestCase(unittest.TestCase):
    def setUp(self):
        self.builder = dic.container.ContainerBuilder()

    def test_resolve_simple_class(self):
        # Arrange
        self.builder.register_class(Standalone)
        container = self.builder.build()

        # Act
        x = container.resolve(Standalone)

        # Assert
        self.assertIsInstance(x, Standalone)

    def test_resolve_with_basic_dep(self):
        # Arrange
        self.builder.register_class(Standalone)
        self.builder.register_class(SimpleComponent)
        container = self.builder.build()

        # Act
        x = container.resolve(SimpleComponent)

        # Assert
        self.assertIsInstance(x, SimpleComponent)
        self.assertIsInstance(x.standalone, Standalone)

    def test_resolve_throws_with_missing_dep(self):
        # Arrange
        self.builder.register_class(SimpleComponent)
        container = self.builder.build()

        # Act
        # Assert
        with self.assertRaises(dic.container.DependencyResolutionError) as cm:
            container.resolve(SimpleComponent)

if __name__ == '__main__':
    unittest.main()