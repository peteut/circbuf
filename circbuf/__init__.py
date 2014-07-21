import sys
import operator
import functools
import itertools
import threading
try:
    import contextlib2 as contextlib
    from collections import Iterable
except ImportError:
    import contextlib
    from collections.abc import Iterable
from contextlib import contextmanager


__all__ = ('ResourceManager', 'CircBuf', 'recv', 'seek_to_pattern')


def _require_lock(name):
    '''Ensure :class:`threading.Lock` is acquired.
    '''
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self = args[0]
            if not getattr(self, name).locked():
                raise RuntimeError('{1} must be acquired prior calling {0}'
                                   .format('.'.join((self.__class__.__name__,
                                                     func.__name__)), name))
            return func(*args, **kwargs)
        return wrapper
    return decorator


class ResourceManager:
    '''Context manager that accepts acquisition and release functions,
    along with an optinal validation function.
    '''

    __slots__ = ('_acquire_resource', '_release_resource',
                 '_check_resource_ok')

    def __init__(self, acquire_resource, release_resource,
                 check_resource_ok=None):
        self._acquire_resource = acquire_resource
        self._release_resource = release_resource
        self._check_resource_ok = check_resource_ok

    def __enter__(self):
        resource = self._acquire_resource()
        if self._check_resource_ok is not None:
            with contextlib.ExitStack() as stack:
                stack.push(self)
                if not self._check_resource_ok(resource):
                    msg = 'Validation failed for {!r}'
                    raise RuntimeError(msg.format(resource))
                # The validation check passed and didn't raise an exception,
                # keep the resource, and pass it back to our caller.
                stack.pop_all()
        return resource

    def __exit__(self, *exc):
        self._release_resource()


class CircBuf(Iterable):
    '''An implementation of a circular buffer, derived from
    `include/linux/circ_buf.h`_.

    .. _`include/linux/circ_buf.h`:
        https://github.com/torvalds/linux/blob/v3.2/include/linux/circ_buf.h
    '''

    __slots__ = ('_buf', '_head', '_tail', '_consumer_lock', '_producer_lock',
                 '__consumer_mv', '__producer_mv')

    def __init__(self, size=2 ** 12):
        if size & (size - 1):
            raise ValueError('size must be power of 2')
        self._buf = bytearray(size)
        self._head = 0
        self._tail = 0
        self._consumer_lock = threading.Lock()
        self._producer_lock = threading.Lock()

    def __len__(self):
        ''':returns: count in buffer
        '''
        head, tail, size = self._head, self._tail, self.capacity
        return (head - tail) & (size - 1)

    @property
    def capacity(self):
        ''':returns: buffer length
        '''
        return len(self._buf)

    @property
    def cnt_to_end(self):
        ''':returns: count up to the end of the buffer
        '''
        head, tail, size = self._head, self._tail, self.capacity
        end = size - tail
        n = (head + end) & (size - 1)
        return n if n < end else end

    @property
    def space_to_end(self):
        ''':returns: space available up to the end of the buffer
        '''
        head, tail, size = self._head, self._tail, self.capacity
        end = size - 1 - head
        n = (end + tail) & (size - 1)
        return n if n <= end else end + 1

    def _producer_mv(self):
        buf, head = self._buf, self._head
        return memoryview(buf)[head: head + self.space_to_end]

    def _consumer_mv(self):
        buf, tail = self._buf, self._tail
        return memoryview(buf)[tail:tail + self.cnt_to_end]

    @property
    def space_avail(self):
        ''':returns: number of bytes available in the buffer
        '''
        return self.capacity - 1 - len(self)

    @property
    def producer_buf(self):
        ''':returns: producer buffer
        :rtype: :class:`memoryview`
        '''
        def acquire():
            self._producer_lock.acquire()
            self.__producer_mv = self._producer_mv()
            return self.__producer_mv

        def release():
            self.__producer_mv.release()
            self._producer_lock.release()

        return ResourceManager(acquire, release)

    @property
    def consumer_buf(self):
        ''':returns: consumer buffer
        :rtype: :class:`memoryview`
        '''
        def acquire():
            self._consumer_lock.acquire()
            self.__consumer_mv = self._consumer_mv()
            return self.__consumer_mv

        def release():
            self.__consumer_mv.release()
            self._consumer_lock.release()

        return ResourceManager(acquire, release)

    @_require_lock('_producer_lock')
    def produced(self, cnt):
        ''':param cnt: written bytes
        :returns: written bytes
        '''
        if cnt > self.space_to_end:
            raise ValueError('cnt bigger than buffer length')
        self._head = (self._head + cnt) & (self.capacity - 1)
        return cnt

    @_require_lock('_consumer_lock')
    def consumed(self, cnt):
        ''':param cnt: consumed bytes
        :returns: consumed bytes
        '''
        if cnt > len(self):
            raise ValueError('cnt bigger than buffer length')
        self._tail = (self._tail + cnt) & (self.capacity - 1)
        return cnt

    def __iter__(self):

        def generator():

            def acquire():
                self._consumer_lock.acquire()
                return self._consumer_mv()

            def release():
                self._consumer_lock.release()

            with ResourceManager(acquire, release) as mv:
                try:
                    for val in map(operator.itemgetter(0), mv):
                        self.consumed(1)
                        yield val
                except TypeError:
                    for val in bytes(mv):
                        self.consumed(1)
                        yield val

            if len(self):
                generator()

        return generator()


    def write(self, b):
        ''':param b: ``bytes`` to ``bytearray`` to write
        :returns: number of bytes written
        '''
        def do(written):
            with self.producer_buf as mv:
                length = min(map(len, (mv, b[written:])))
                if not length:
                    return written
                mv[: length] = b[: length]
                self.produced(length)
            written += length
            if written == towrite or length == 0:
                return written
            return do(written)

        if not min(self.space_avail, len(b)):
            return None

        towrite = len(b)
        result = do(0)

        return result if result else None


def recv(buf, fn, *args):
    '''Helper to read from a function which receives into buf

    :param buf: buffer to receive into
    :param fn: receive function, accepts a buffer as first argument
    to read into and returns the number of bytes received
    :param args: arguments for `fn`
    '''
    with buf.producer_buf as mv:
        buf.produced(fn(mv, *args))


@contextmanager
def _ignored(*exceptions):
    try:
        yield
    except exceptions:
        pass


def seek_to_pattern(buf, pattern):
    '''Helper to seek buf to pattern

    :param buf: buffer to seek to pattern
    :param pattern: pattern to seek to
    :returns: remaining buf length
    '''
    def check_pattern(it, pattern):
        ch = next(it)
        if ch != pattern[0]:
            return
        return True if len(pattern) == 1 else check_pattern(it, pattern[1:])

    if not isinstance(pattern, Iterable):
        pattern = (pattern,)

    try:
        while True:
            it = itertools.dropwhile(
                functools.partial(operator.ne, pattern[0]), buf)
            if check_pattern(it, pattern):
                return len(buf)
    except StopIteration:
        pass

    return len(buf)
