=============
Relationships
=============
Relationships are 'special' dependencies that model something more complex than `A` depends on `B`. As you'd expect, scopes are respected.

Factory
=======
A ``dic.rel.Factory`` relationship can be used when you want to be able to create dependencies from a class, without depending on the dic container directly.

For example:
.. sourcecode:: python

    class Part(object):
        pass

    class BuildsStuff(object):
        def __init__(self, part_factory: dic.rel.Factory(Part))
            self.part_factory = part_factory

        def make_me_one(self):
            return self.part_factory()

Custom Arguments
----------------
It's possible to specify custom arguments when invoking a factory, the arguments will be used:

1. When the dependency isn't registered in the container; or
2. To override a resolve operation for something that is registered in the container

An example of the first:

.. sourcecode:: python

    class Part(object):
        def __init__(self, name):
            self.name = name

    class BuildsStuff(object):
        def __init__(self, part_factory: dic.rel.Factory(Part))
            self.part_factory = part_factory

        def make_me_one_with_a_name(self, name):
            return self.part_factory(name=name)

    # can then resolve just BuildsStuff

Lazy
====
A ``dic.rel.Lazy`` relationship can be used where you want a component, but not yet. For example for breaking circular resolve dependencies. Lazy is implemented in a thread-safe way, so
multiple threads will get the same instance.

.. sourcecode:: python

    class EventuallyNeeded(object):
        def do_it(self):
            pass

    class EventuallyWantsYou(object):
        def __init__(self, eventually_needed: dic.rel.Lazy(EventuallyNeeded)):
            self.eventually_needed = eventually_needed

        def ok_ready(self, name):
            # EventuallyNeeded will be created here (rather than directly injected in to the constructor)
            self.eventually_needed.instance.do_it()

