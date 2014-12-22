=======
Samples
=======

dic includes several samples, see the `github repository`_.

CherryPy Songs
==============
Extending the `CherryPy songs tutorial`_:

.. literalinclude:: ../samples/cherrypy-songs-tutorial/songs.py

Mocking
=======
dic wouldn't be very useful if it didn't help you test your code. A full example of using dic to inject mocks during tests:

This sample shows:
1. Mocking the `database` from a `service
2. Using the new Python 3.3 mocking library (``unittest.mock``)

.. literalinclude:: ../samples/mocking/mocking.py

.. _`github repository`: https://github.com/zsims/dic
.. _`CherryPy songs tutorial`: https://cherrypy.readthedocs.org/en/3.3.0/tutorial/REST.html#getting-started
