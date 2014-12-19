import abc
import inspect
from . import rel
from . import scope


class DependencyResolutionError(Exception):
    pass


class ComponentRegistration(metaclass=abc.ABCMeta):
    def __init__(self, component_scope):
        self.component_scope = component_scope

    @abc.abstractmethod
    def _create(self, container):
        """
        Creates a new instance of the component using the given container
        to resolve dependencies regardless of the scope.
        :param container: The container to resolve dependencies from.
        :return: An instance of the component.
        """
        pass

    def create(self, container):
        """
        Creates a new instance of the component, respecting the scope.
        :param container: The container to resolve dependencies from.
        :return: An instance of the component.
        """
        return self.component_scope.instance(lambda: self._create(container))


class ConstructorRegistration(ComponentRegistration):
    """
    Creates a component via the constructor.
    """
    def __init__(self, class_type, scope):
        super().__init__(scope)

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

    def _create(self, container):
        argument_map = {}
        for (arg_name, arg_type) in self.argument_types.items():
            argument_map[arg_name] = container.resolve(arg_type)

        return self.class_type(**argument_map)


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

    def resolve(self, component_type):
        """
        Resolves an instance of the component type.
        :param component_type: The type of the component (e.g. a class)
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
        return self.registry_map[component_type].create(self)


class ContainerBuilder(object):
    """
    Builds a container from the registered configuration.
    """
    def __init__(self):
        self.registry = {}

    def register_class(self, class_type, component_scope=scope.InstancePerDependency):
        """
        Registers the given class for creation via its constructor.
        :param class_type: The class type.
        :param component_scope: The scope of the component, defaults to instance per dependency.
        """
        self.registry[class_type] = ConstructorRegistration(class_type, component_scope())

    def build(self):
        """
        Builds a new container using the registered components.
        :return: A container
        """
        return Container(self.registry)
