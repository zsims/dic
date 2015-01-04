import dic
import threading
import time
import unittest


class Standalone(object):
    pass


class SpecialStandalone(Standalone):
    pass


class SimpleComponent(object):
    def __init__(self, s: Standalone):
        self.standalone = s


class SimpleModule(dic.container.Module):
    def load(self, builder):
        builder.register_class(Standalone)


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

    def test_register_class_defaults_instance_per_dep(self):
        # Arrange
        self.builder.register_class(Standalone)

        # Act
        container = self.builder.build()

        # Assert
        self.assertIsInstance(container.registry_map[Standalone].component_scope, dic.scope.InstancePerDependency)

    def test_register_as_another_type(self):
        # Arrange
        self.builder.register_class(SpecialStandalone, register_as=Standalone)

        # Act
        container = self.builder.build()

        # Assert
        self.assertIn(Standalone, container.registry_map)

    def test_register_as_other_types(self):
        # Arrange
        self.builder.register_class(SpecialStandalone, register_as=(Standalone, 'x'))

        # Act
        container = self.builder.build()

        # Assert
        self.assertIn(Standalone, container.registry_map)
        self.assertIn('x', container.registry_map)

    def test_register_callback(self):
        # Arrange
        self.builder.register_callback(SimpleComponent, lambda c: SimpleComponent(c.resolve(Standalone)))

        # Act
        container = self.builder.build()

        # Assert
        self.assertIn(SimpleComponent, container.registry_map)
        self.assertNotIn(Standalone, container.registry_map)

    def test_register_overrides_previous_registration(self):
        # Arrange
        standalone = Standalone()
        self.builder.register_instance(Standalone, standalone)

        # Act
        # This should dis-regard the existing instance registration
        self.builder.register_class(Standalone)

        # Assert
        container = self.builder.build()

        x = container.resolve(Standalone)
        self.assertIsNot(x, standalone)
        y = container.resolve(Standalone)
        self.assertIsNot(x, y)

    def test_built_containers_are_isolated(self):
        # Arrange
        self.builder.register_class(Standalone, component_scope=dic.scope.SingleInstance)

        first_container = self.builder.build()
        second_container = self.builder.build()

        # Act
        first = first_container.resolve(Standalone)
        first_prime = first_container.resolve(Standalone)
        second = second_container.resolve(Standalone)
        second_prime = second_container.resolve(Standalone)

        # Assert
        self.assertIs(first, first_prime)
        self.assertIsNot(first, second)
        self.assertIs(second, second_prime)

    def test_register_module(self):
        # Arrange/Act
        self.builder.register_module(SimpleModule())
        container = self.builder.build()

        # Assert
        self.assertIn(Standalone, container.registry_map)


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

    def test_resolve_single_instance(self):
        # Arrange
        self.builder.register_class(Standalone, component_scope=dic.scope.SingleInstance)
        container = self.builder.build()

        # Act
        x = container.resolve(Standalone)
        y = container.resolve(Standalone)

        # Assert
        self.assertIs(x, y)

    def test_resolve_custom_tag(self):
        # Note that this isn't an advertised feature of dic, but still good to test.
        self.builder.register_class(Standalone, component_scope=dic.scope.SingleInstance, register_as='X')
        self.builder.register_class(Standalone, component_scope=dic.scope.SingleInstance, register_as='Y')
        container = self.builder.build()

        # Act
        x = container.resolve('X')
        y = container.resolve('Y')

        # Assert
        self.assertIsNot(x, y)
        self.assertIsInstance(x, Standalone)
        self.assertIsInstance(y, Standalone)

    def test_resolve_dep_single_instance(self):
        # Arrange
        self.builder.register_class(Standalone, component_scope=dic.scope.SingleInstance)
        self.builder.register_class(SimpleComponent)
        container = self.builder.build()

        # Act
        x = container.resolve(SimpleComponent)
        y = container.resolve(Standalone)

        # Assert
        self.assertIs(x.standalone, y)

    def test_resolve_instance_per_dep(self):
        # Arrange
        self.builder.register_class(Standalone)
        container = self.builder.build()

        # Act
        x = container.resolve(Standalone)
        y = container.resolve(Standalone)

        # Assert
        self.assertIsNot(x, y)

    def test_resolve_via_alias(self):
        # Arrange
        self.builder.register_class(SpecialStandalone, register_as=[Standalone])
        container = self.builder.build()

        # Act
        x = container.resolve(Standalone)

        # Assert
        self.assertIsInstance(x, SpecialStandalone)

    def test_resolve_with_callback(self):
        # Arrange
        standalone = Standalone()
        self.builder.register_callback(SimpleComponent, lambda c: SimpleComponent(standalone))
        container = self.builder.build()

        # Act
        component = container.resolve(SimpleComponent)

        # Assert
        self.assertIs(component.standalone, standalone)

    def test_resolve_callback_respects_scope(self):
        # Arrange
        self.builder.register_class(Standalone, component_scope=dic.scope.SingleInstance)
        self.builder.register_callback(SimpleComponent, lambda c: SimpleComponent(c.resolve(Standalone)))
        container = self.builder.build()

        # Act
        component1 = container.resolve(SimpleComponent)
        component2 = container.resolve(SimpleComponent)

        # Assert
        self.assertIsNot(component1, component2)
        self.assertIs(component1.standalone, component2.standalone)

    def test_resolve_instance(self):
        # Arrange
        standalone = Standalone()
        self.builder.register_instance(Standalone, standalone)
        container = self.builder.build()

        # Act
        x = container.resolve(Standalone)
        y = container.resolve(Standalone)

        # Assert
        self.assertIs(x, standalone)
        self.assertIs(y, standalone)

    def test_resolve_thread_safe(self):
        # Obviously can't test this 100%, but should be enough to see if
        # it has been done right-ish...

        # Arrange
        finish_first = threading.Event()
        did_first = threading.Event()
        did_second = threading.Event()
        expected_first = Standalone()
        expected_second = Standalone()
        actual = [None, None]

        # DODO THIS IS
        def resolve_standalone(component_context):
            if actual[0] is None:
                actual[0] = expected_first
                did_first.set()
                # This should cause the container to lock when resolving the second thing
                finish_first.wait()
            elif actual[1] is None:
                actual[1] = expected_second
                did_second.set()

        self.builder.register_callback(Standalone, resolve_standalone)
        container = self.builder.build()

        # Act/Assert
        threading.Thread(target=container.resolve, args=(Standalone,)).start()
        threading.Thread(target=container.resolve, args=(Standalone,)).start()

        time.sleep(2)
        self.assertTrue(did_first.is_set())
        self.assertIs(expected_first, actual[0])
        self.assertFalse(did_second.is_set())

        # finish the first resolve
        finish_first.set()

        # wait for the second resolve to finish
        did_second.wait(timeout=2)
        self.assertIs(expected_second, actual[1])

if __name__ == '__main__':
    unittest.main()
