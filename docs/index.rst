CircBuf - Circular Buffer For Python
====================================

``circbuf`` implements a circular buffer for Python.
It allows for zero copy operation, i.e. it uses ``memoryview``
to expose consumer and producer buffers.
Access to the buffer is synchronised by locks, managed by context managers.

Example
-------

.. code-block:: python

    import circbuf

    buf = circbuf.CircBuf()
    # Produce data
    with buf.producer_buf as mv:
        mv[0] = 42
        buf.produced(1)

    print('First entry: {}'.format(next(iter(buf)))) # First entry: 42

Features
--------

* Pure Python
* Minimises allocation of big memory chunks
* Automatic access synchronisation
* Tested on Python 3.2, 3.3, 3.4



Install it with ``pip``:

.. code-block:: console

    $ pip install circbuf

Contents
--------

.. toctree::
    :maxdepth: 2

    api-reference


Useful Links
------------

* `circbuf.h`_
* `memoryview`_

.. _`circbuf.h`: https://github.com/torvalds/linux/blob/master/include/linux/circ_buf.h
.. _`memoryview`: https://docs.python.org/3.4/library/stdtypes.html#memoryview)
