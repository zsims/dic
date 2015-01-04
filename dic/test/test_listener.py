import dic
import unittest
import mock


class Atom(object):
    pass


class Part(object):
    def __init__(self, atom1: Atom, atom2: Atom):
        pass


class Factory(object):
    def __init__(self, part_factory: dic.rel.Factory(Part)):
        self._part_factory = part_factory

    def make(self):
        return self._part_factory()


class ListenerTestCase(unittest.TestCase):
    def setUp(self):
        builder = dic.container.ContainerBuilder()
        builder.register_class(Factory)
        builder.register_class(Part)
        builder.register_class(Atom)

        self.container = builder.build()
        self.container.listener = mock.Mock(spec=dic.listener.ContainerListener)
        self.listener_mock = self.container.listener

    def test_listener_resolve_simple(self):
        # Arrange
        # Act
        self.container.resolve(Atom)

        # Assert
        self.listener_mock.resolve_started.assert_called_once_with(mock.ANY, Atom)
        self.listener_mock.resolve_succeeded.assert_called_once_with(mock.ANY, Atom)

    def test_listener_nested_resolve(self):
        # Arrange
        # Act
        self.container.resolve(Factory)

        # Assert
        started_calls = [
            mock.call(mock.ANY, Factory),
            mock.call(mock.ANY, Part),
            mock.call(mock.ANY, Atom),
        ]

        succeeded_calls = [
            mock.call(mock.ANY, Factory),
            mock.call(mock.ANY, Part),
            mock.call(mock.ANY, Atom)
        ]

        self.listener_mock.resolve_started.assert_has_calls(started_calls)
        self.listener_mock.resolve_succeeded.assert_has_calls(succeeded_calls)

if __name__ == '__main__':
    unittest.main()