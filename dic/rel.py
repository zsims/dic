class Relationship(object):
    def __init__(self):
        self._container = None


class FactoryRelationship(Relationship):
    def __init__(self, component_type):
        super().__init__()
        self.component_type = component_type

    def __call__(self, *args, **kwargs):
        return self._container.resolve(self.component_type)


def factory(component_type):
    """
    Models a factory relationship capable of creating the given type. The scope of the registered component is
    respected. Meaning a SingleInstance registration will return the same instance for multiple factory calls.
    :param component_type:
    :return: A factory relationship
    """
    return FactoryRelationship(component_type)


class LazyRelationship(Relationship):
    def __init__(self, component_type):
        super().__init__()
        self.component_type = component_type
        self._component = None

    @property
    def has_value(self):
        return self._component is not None

    @property
    def value(self):
        if self._component is None:
            self._component = self._container.resolve(self.component_type)
        return self._component


def lazy(component_type):
    """
    Models a lazy relationship. Dependency lookup is delayed until the value is resolved for the first time.
    :param component_type: The component type.
    :return: A lazy relationship
    """
    return LazyRelationship(component_type)

