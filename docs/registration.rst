============
Registration
============
In order to create a dependency container, components must be registered within a ``dic.container.ContainerBuilder``. The container builder
controls how components will be resolved. Consider a builder as a 'spec' for how the container should be built.

Some key points:

1. The order of registration does not matter
2. A container builder may build multiple containers, each of which will be independent

Registering Classes
===================
Core to dic is class registration. dic uses Python 3 annotations to provide 'hints' for the types of dependencies that components require. The annotations
provide a 'compile safe' way of referencing types without creating any hard dependencies on the container, or other dic types.

.. sourcecode:: python

    class OtherDependency(object):
        pass

    class MyClass(object):
        def __init__(self, dependency: OtherDependency):
            pass

    builder = dic.container.ContainerBuilder()
    builder.register_class(MyClass)
    builder.register_class(OtherDependency)

    container = builder.build()
    # use the container

A ``dic.container.DependencyResolutionError`` will be raised during a ``.resolve(...)`` call if an annotation is provided, but no component registered.

Registering Instances
=====================
An already-created dependency can be registered directly. This is useful if you're integrating with other projects, or migrating to dic.

.. sourcecode:: python

    class MyExternalThing(object):
        pass

    instance = MyExternalThing()

    builder = dic.container.ContainerBuilder()
    builder.register_instance(MyExternalThing, instance)

    container = builder.build()
    # use the container

Note that:
1. Scopes do not apply to components registered in this way
2. Aliases can still be specified with the ``register_as`` argument

Custom Registration
===================
Lastly, a callback can be provided to create components in any way you want. This provides a good way of integrating things that don't play nicely with dic, or
components that you don't have control of.

1. Scopes are respected
2. Aliases can still be specified with the ``register_as`` argument
3. The callback is called with a `component context` that can be used to resolve other dependencies. Do not store this context, as it can only be used for the scope of the
context callback.

.. sourcecode:: python

    class MyExternalThing(object):
        pass

    def create_my_thing(component_context):

    builder = dic.container.ContainerBuilder()
    builder.register_instance(MyExternalThing, instance)

    container = builder.build()
    # use the container

Aliases (register_as)
=====================
It's possible to register callbacks and classes under multiple types. This is useful if you want a specialised implementation available as its base class.

.. sourcecode:: python

    class BaseDependency(object):
        pass

    class SpecialDependency(BaseDependency):
        pass

    class MyClass(object):
        def __init__(self, dependency: BaseDependency):
            pass

    builder = dic.container.ContainerBuilder()
    builder.register_class(MyClass)
    builder.register_class(SpecialDependency, register_as=[BaseDependency])

    container = builder.build()
    # use the container

Scopes
======
Scopes model how long resolved components should live for.

Instance Per Dependency (Default)
---------------------------------
The default scope is to create a new instance each time the component is resolved.

.. sourcecode:: python

    class ManyOfThese(object):
        pass

    builder = dic.container.ContainerBuilder()
    # this is the default, but shows how the scope can be set
    builder.register_class(ManyOfThese, component_scope=dic.scope.InstancePerDependency)

    container = builder.build()
    # use the container

Single Instance
---------------
Models a 'singleton', no matter how many times the component is resolved, only one instance will be created.

.. sourcecode:: python

    class OneOfThese(object):
        pass

    builder = dic.container.ContainerBuilder()
    builder.register_class(OneOfThese, component_scope=dic.scope.SingleInstance)

    container = builder.build()
    # use the container
    only_one = container.resolve(OneOfThese)
    other_only_one = container.resolve(OneOfThese)

    # only_one is the same instance as other_only_one

Custom Scopes
-------------
Scopes are highly extensible, it's possible to create new scopes by deriving from ``dic.scope.Scope``.

For example, a scope that creates a dependency per calling thread may look like:

.. sourcecode:: python

    class ThreadingScope(dic.scope.Scope):
        def __init__(self)
            # thread -> instance
            self._instances = {}
            self._scope_lock = threading.RLock()

        def instance(self, create_function):
            with self._scope_lock:
                thread_id = threading.current_thread().ident
                if thread_id not in self.instances:
                    self._instances[thread_id] = create_function()
                return self._instances[thread_id]


    # use the scope
    builder = dic.container.ContainerBuilder()
    builder.register_class(MyClass, component_scope=ThreadingScope)
    # ...

Note that the above is a sample. The may instances live beyond the threads.
