# Shows how unittest.mock can be used with dic to mock components during testing

import dic
import unittest, unittest.mock


class Database(object):
    def __init__(self):
        self.data = {
            '1': 'some data',
            '2': 'other data',
        }

    def get_data(self):
        return self.data


class Service(object):
    def __init__(self, database: Database):
        self.database = database

    def load(self):
        return self.database.get_data()


class ServiceTestCase(unittest.TestCase):
    """
    Test case for `Service` that mocks out the database.
    """
    def setUp(self):
        builder = dic.container.ContainerBuilder()
        builder.register_class(Service)

        # register a mock instead of the real database
        self.database_mock = unittest.mock.Mock(spec=Database)
        builder.register_instance(Database, self.database_mock)
        container = builder.build()

        self.service = container.resolve(Service)

    def test_get_data(self):
        # Arrange
        attrs = {'get_data.return_value': {'3': 'mocked data'}}
        self.database_mock.configure_mock(**attrs)

        # Act
        self.service.load()

        # Assert
        self.database_mock.get_data.called_once_with()

if __name__ == '__main__':
    unittest.main()
