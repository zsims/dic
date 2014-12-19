class Relationship(object):
    def __init__(self):
        self._container = None


class Factory(Relationship):
    """
    Models a factory relationship capable of creating the given type. The scope of the registered component is
    respected. Meaning a SingleInstance registration will return the same instance for multiple factory calls.
    """
    def __init__(self, component_type):
        super().__init__()
        self.component_type = component_type

    def __call__(self, *args, **kwargs):
        return self._container.resolve(self.component_type)


class Lazy(Relationship):
    """
    Models a lazy relationship. Dependency lookup is delayed until the value is resolved for the first time.
    """
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

