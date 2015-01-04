import abc
import copy
import inspect
import threading
from . import rel
from . import scope


class DependencyResolutionError(Exception):
    pass


class _ComponentRegistration(metaclass=abc.ABCMeta):
    def __init__(self, component_scope):
        self.component_scope = component_scope

    @abc.abstractmethod
    def _create(self, component_context, overriding_args):
        """
        Creates a new instance of the component using the given container
        to resolve dependencies regardless of the scope.
        :param component_context: The context to resolve dependencies from.
        :param overriding_args: Overriding arguments to use (by name) instead of resolving them.
        :return: An instance of the component.
        """
        pass

    def create(self, component_context, overriding_args):
        """
        Creates a new instance of the component, respecting the scope.
        :param component_context: The context to resolve dependencies from.
        :param overriding_args: Overriding arguments to use (by name) instead of resolving them.
        :return: An instance of the component.
        """
        return self.component_scope.instance(lambda: self._create(component_context, overriding_args))


class _ConstructorRegistration(_ComponentRegistration):
    """
    Creates a component via the constructor.
    """
    def __init__(self, class_type, component_scope):
        super().__init__(component_scope)

        self.class_type = class_type
        # map of argument name -> argument type
        self.argument_types = {}

        self._inspect_constructor()

    def _find_constructor(self):
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

    def _inspect_constructor(self):
        constructor = self._find_constructor()
        if constructor is not None:
            self.argument_types = constructor.__annotations__

    def _create(self, component_context, overriding_args):
        argument_map = overriding_args or {}
        for (arg_name, arg_type) in self.argument_types.items():
            # not already provided, try resolve the argument
            if arg_name not in argument_map:
                argument_map[arg_name] = component_context.resolve(arg_type)

        return self.class_type(**argument_map)


class _CallbackRegistration(_ComponentRegistration):
    def __init__(self, callback, component_scope):
        super().__init__(component_scope)
        self._callback = callback

    def _create(self, component_context, overriding_args):
        return self._callback(component_context)


class _InstanceRegistration(_ComponentRegistration):
    def __init__(self, instance):
        # the scope doesn't matter, but SingleInstance is what it'll always be
        super().__init__(scope.SingleInstance())
        self._instance = instance

    def _create(self, component_context, overriding_args):
        return self._instance

    def __deepcopy__(self, memo):
        # We don't want to have this copy self._instance when building the container from a builder
        return self


class _ComponentContext(object):
    """
    The context of a component resolve operation.
    A context will be created from a top-level resolve, and then all dependencies will be resolved within that context.
    """
    def __init__(self, container):
        self._container = container

    def resolve(self, component_type, **kwargs):
        # TODO: split off _container, even though we're an internal class. Still isn't great.
        if isinstance(component_type, rel.Relationship):
            # expand the relationship
            # note that relationships get the container as they're all currently lazy
            # this *could* support the context in future, but the context shouldn't be stored
            return component_type.resolve(self._container)

        # normal component
        if component_type not in self._container.registry_map:
            raise DependencyResolutionError(
                "The requested type %s was not found in the container. Is it registered?" % component_type.__name__)

        registration = self._container.registry_map[component_type]
        return registration.create(self, kwargs)


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
        # The resolve lock is recursive as a constructor may call a factory (which calls container.resolve()),
        # without a recursive lock, this would be a deadlock
        self._resolve_lock = threading.RLock()

    def resolve(self, component_type, **kwargs):
        """
        Resolves an instance of the component type.
        :param component_type: The type of the component (e.g. a class).
        :param kwargs: Overriding arguments to use (by name) instead of resolving them.
        :return: An instance of the component.
        """
        with self._resolve_lock:
            context = _ComponentContext(self)
            return context.resolve(component_type, **kwargs)


class Module(metaclass=abc.ABCMeta):
    """
    Module to help structure building of the container.
    """
    @abc.abstractmethod
    def load(self, builder):
        """
        Register dependencies from this module.
        :param builder: The container builder to register components to.
        """
        pass


class ContainerBuilder(object):
    """
    Builds a container from the registered configuration.
    """
    def __init__(self):
        self.registry = {}

    def _register(self, class_type, registration, register_as):
        if register_as is None:
            register_as = class_type

        # if we didn't get a tuple or a list, put it in a lists
        if type(register_as) is not list and type(register_as) is not tuple:
            register_as = [register_as]

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
        :param callback: The function to call to create/get an instance, of the form fn(component_context)
        :param component_scope: The scope of the component, defaults to instance per dependency.
        :param register_as: The types to register the class as, defaults to the given class_type.
        """
        registration = _CallbackRegistration(callback, component_scope())
        self._register(class_type, registration, register_as)

    def register_instance(self, class_type, instance, register_as=None):
        """
        Registers the given instance (already created).
        :param class_type: The class type.
        :param instance: The instance to register.
        :param register_as: The types to register the class as, defaults to the given class_type.
        """
        registration = _InstanceRegistration(instance)
        self._register(class_type, registration, register_as)

    def register_module(self, module):
        """
        Registers the module instance.
        :param module: The module to register.
        """
        module.load(self)

    def build(self):
        """
        Builds a new container using the registered components.
        :return: A container
        """
        # copy the registry so built containers are isolated
        registry_copy = copy.deepcopy(self.registry)
        return Container(registry_copy)
