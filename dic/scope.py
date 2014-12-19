import abc


class Scope(metaclass=abc.ABCMeta):
    """
    Controls the lifetime scope of a component registration.
    """
    @abc.abstractmethod
    def instance(self, container, registration):
        """
        Gets the instance of the component given its registration.
        :param registration: The component registration
        :return: The instance
        """
        pass


class InstancePerDependency(Scope):
    """
    Creates an instance per dependency
    """
    def instance(self, container, registration):
        return registration.create(container)


class SingleInstance(Scope):
    def __init__(self):
        self.component_instance = None

    def instance(self, container, registration):
        if self.component_instance is None:
            self.component_instance = registration.create(container)
        return self.component_instance
