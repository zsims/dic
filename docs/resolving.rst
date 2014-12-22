=========
Resolving
=========

Once a ``dic.container.Container`` has been built via the :doc:`container builder <registration>`, it's ready for use. Generally you'll resolve your application 'bootstrapper' after building the container.

Components can be directly resolved from the container:

.. sourcecode:: python

    class MyClass(object):
        pass

    builder = dic.container.ContainerBuilder()
    builder.register_class(MyClass)

    container = builder.build()

    # factory to create MyClass
    factory = container.resolve(dic.rel.Factory(MyClass))

    # or instances
    instance = container.resolve(MyClass)

Circular Dependencies
=====================
dic does **not** yet have 'circular dependency' detection yet, this means if a relationship like this is resolved it will likely crash.

Thread Safety
=============
``dic.container.Container.resolve()`` is thread-safe. Also see registration for implications with the callback resolve function ``.register_callback()``.

