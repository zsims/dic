import abc


class Scope(metaclass=abc.ABCMeta):
    """
    Controls the lifetime scope of a component registration.
    """
    @abc.abstractmethod
    def instance(self, create_function):
        """
        Gets the instance of the component given its registration.
        :param create_function: The function to create a new component, if required.
        :return: The instance
        """
        pass


class InstancePerDependency(Scope):
    """
    Creates an instance per dependency
    """
    def instance(self, create_function):
        return create_function()


class SingleInstance(Scope):
    def __init__(self):
        self.component_instance = None

    def instance(self, create_function):
        if self.component_instance is None:
            self.component_instance = create_function()
        return self.component_instance
