dic
===

Dependency Injection Container for Python 3+ influenced partially by Autofac_. dic aims to be a tiny framework to help
you build software.

dic uses Python 3 annotations to provide hints for the components that should be injected.

Currently, dic supports:

1. Constructor injection for classes
2. Factory and Lazy relationships
3. Registration via:
    1. Constructor matching for a registered class
    2. Custom callback
4. Lifetime scopes:
    1. Instance per dependency
    2. Single instance

Quick Example
=============
A quick example on how to use dic:
 ::

    import dic

    class SimpleThing(object):
        def say(self, message):
            print(message)

    class RequiresThing(object):
        def __init__(self, thing: SimpleThing):
            self.thing = thing

        def say(self, message):
            self.thing.say(message)

    # build the container
    builder = dic.container.ContainerBuilder()

    builder.register_class(SimpleThing)
    builder.register_class(RequiresThing, component_scope=dic.scope.SingleInstance)

    container = builder.build()

    # use the container

    # Note there'll only be one of these due to SingleInstance scoping during build
    x = container.resolve(RequiresThing)
    x.say("my message")

Relationships
=============
dic supports basic relationships:

1. `dic.rel.Lazy` - don't create the dependency until it's first used
2. `dic.rel.Factory` - the component wants to create other components. Lifetime scopes are respected.

Using a factory:
 ::

    import dic

    class SimpleThing(object):
        pass

    class BuildsThings(object):
        def __init__(self, thing_factory: dic.rel.Factory(SimpleThing)):
            self.thing_factory = thing_factory

        def build_me_a_thing(self):
            # builds a new thing using the injected factory
            self.thing_factory()

    # build the container
    builder = dic.container.ContainerBuilder()

    builder.register_class(SimpleThing)
    builder.register_class(BuildsThing)

    container = builder.build()

    # use the container

    x = container.resolve(BuildsThing)

    #
    thing = x.build_me_a_thing()
    # ...


FAQ
===

1. Is dic thread-safe?

 Not yet. There's plans to make it thread-safe.

2. Can I define my own scopes?

 Yes. Derive a scope from `dic.scope.Scope`. Scopes can be used to provide lifetime for a calling thread, for example

3. Will you support feature "X"?

 The philosophy of dic is to remain small, but extensible -- e.g. remain "out of the way." So likely not.

.. _Autofac: http://autofac.org/
