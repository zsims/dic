import abc
import inspect
from . import rel
from . import scope


class DependencyResolutionError(Exception):
    pass


class _ComponentRegistration(metaclass=abc.ABCMeta):
    def __init__(self, component_scope):
        self.component_scope = component_scope

    @abc.abstractmethod
    def _create(self, container, overriding_args):
        """
        Creates a new instance of the component using the given container
        to resolve dependencies regardless of the scope.
        :param container: The container to resolve dependencies from.
        :param overriding_args: Overriding arguments to use (by name) instead of resolving them.
        :return: An instance of the component.
        """
        pass

    def create(self, container, overriding_args):
        """
        Creates a new instance of the component, respecting the scope.
        :param container: The container to resolve dependencies from.
        :param overriding_args: Overriding arguments to use (by name) instead of resolving them.
        :return: An instance of the component.
        """
        return self.component_scope.instance(lambda: self._create(container, overriding_args))


class _ConstructorRegistration(_ComponentRegistration):
    """
    Creates a component via the constructor.
    """
    def __init__(self, class_type, component_scope):
        super().__init__(component_scope)

        self.class_type = class_type
        # map of argument name -> argument type
        self.argument_types = {}

        self.__inspect_constructor()

    def __find_constructor(self):
        """
        Finds the constructor from the class_type.
        :return: The constructor function.
        """

        def isconstructor(object):
            return inspect.isfunction(object) and object.__name__ == '__init__'

        # find all the dependencies from the constructor
        constructors = inspect.getmembers(self.class_type, predicate=isconstructor)

        if constructors:
            name, func = constructors[0]
            return func

        # No explicit __init__
        return None

    def __inspect_constructor(self):
        constructor = self.__find_constructor()
        if constructor is not None:
            self.argument_types = constructor.__annotations__

    def _create(self, container, overriding_args):
        argument_map = overriding_args or {}
        for (arg_name, arg_type) in self.argument_types.items():
            # not already provided, try resolve the argument
            if arg_name not in argument_map:
                argument_map[arg_name] = container.resolve(arg_type)

        return self.class_type(**argument_map)


class _CallbackRegistration(_ComponentRegistration):
    def __init__(self, callback, component_scope):
        super().__init__(component_scope)
        self.callback = callback

    def _create(self, container, overriding_args):
        return self.callback(container)


class Container(object):
    """
    IoC container.
    """
    def __init__(self, registry_map):
        """
        Creates a new container
        :param registry_map: A map of type -> ComponentRegistration
        """
        self.registry_map = registry_map

    def resolve(self, component_type, **kwargs):
        """
        Resolves an instance of the component type.
        :param component_type: The type of the component (e.g. a class)
        :param kwargs: Overriding arguments to use (by name) instead of resolving them.
        :return: An instance of the component.
        """
        # relationship (always lazy for now)
        if isinstance(component_type, rel.Relationship):
            component_type._container = self
            return component_type

        # normal component
        if component_type not in self.registry_map:
            raise DependencyResolutionError(
                "The requested type %s was not found in the container. Is it registered?" % component_type.__name__)
        return self.registry_map[component_type].create(self, kwargs)


class ContainerBuilder(object):
    """
    Builds a container from the registered configuration.
    """
    def __init__(self):
        self.registry = {}

    def _register(self, class_type, registration, register_as):
        if register_as is None:
            register_as = [class_type]

        for available_as in register_as:
            self.registry[available_as] = registration

    def register_class(self, class_type, component_scope=scope.InstancePerDependency, register_as=None):
        """
        Registers the given class for creation via its constructor.
        :param class_type: The class type.
        :param component_scope: The scope of the component, defaults to instance per dependency.
        :param register_as: The types to register the class as, defaults to the given class_type.
        """
        registration = _ConstructorRegistration(class_type, component_scope())
        self._register(class_type, registration, register_as)

    def register_callback(self, class_type, callback, component_scope=scope.InstancePerDependency, register_as=None):
        """
        Registers the given class for creation via the given callback.
        :param class_type: The class type.
        :param callback: The function to call to create/get an instance, of the form fn(container)
        :param component_scope: The scope of the component, defaults to instance per dependency.
        :param register_as: The types to register the class as, defaults to the given class_type.
        """
        registration = _CallbackRegistration(callback, component_scope())
        self._register(class_type, registration, register_as)

    def build(self):
        """
        Builds a new container using the registered components.
        :return: A container
        """
        return Container(self.registry)
