import abc


class Relationship(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def resolve(self, container):
        """
        Called when the relationship is resolved. E.g. about to be injected.
        """
        pass


class _ResolvedFactory(object):
    """
    Class that will be injected into components when they ask for a factory.
    """
    def __init__(self, container, component_type):
        self._container = container
        self._component_type = component_type

    def __call__(self, *args, **kwargs):
        return self._container.resolve(self._component_type, **kwargs)


class Factory(Relationship):
    """
    Models a factory relationship capable of creating the given type. The scope of the registered component is
    respected. Meaning a SingleInstance registration will return the same instance for multiple factory calls.

    Overriding arguments can be provided.
    """
    def __init__(self, component_type):
        self.component_type = component_type

    def resolve(self, container):
        return _ResolvedFactory(container, self.component_type)


class _ResolvedLazy(object):
    """
    Class that will be injected into components when they ask for a lazy.
    """
    def __init__(self, container, component_type):
        self._container = container
        self._component = None
        self._component_type = component_type
    @property
    def has_value(self):
        return self._component is not None

    @property
    def value(self):
        if self._component is None:
            self._component = self._container.resolve(self._component_type)
        return self._component


class Lazy(Relationship):
    """
    Models a lazy relationship. Dependency lookup is delayed until the value is resolved for the first time.
    """
    def __init__(self, component_type):
        self._component_type = component_type

    def resolve(self, container):
        return _ResolvedLazy(container, self._component_type)

