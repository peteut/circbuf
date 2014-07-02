import collections.abc
import functools
import contextlib
import threading

__all__ = ('ResourceManager', 'CircBuf', 'readinto')

def _require_lock(name):
    '''
    Ensure :class:`threading.Lock` is acquired.
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

    def __init__(self, acquire_resource, release_resource,
                 check_resource=None):
        self._acquire_resource = acquire_resource
        self._release_resource = release_resource
        if check_resource is None:
            def check_resource_ok(resource):
                return True
        self._check_resource = check_resource_ok

    @contextlib.contextmanager
    def _cleanup_on_error(self):
        with contextlib. ExitStack() as stack:
            stack.push(self)
            yield
            # Validation check passed and didn't raise an exception,
            # pass the resource back to our caller.
            stack.pop_all()

    def __enter__(self):
        resource = self._acquire_resource()
        with self._cleanup_on_error():
            if not self._check_resource(resource):
                raise RuntimeError(
                    'Validation failed for {!r}'.format(resource))
        return resource

    def __exit__(self, *exc):
        self._release_resource()



DEFAULT_BUFLEN = 2 ** 12

class CircBuf(collections.abc.Iterable):
    '''
    An implementation of a circular buffer, derived from
    `include/linux/circ_buf.h`_.

    .. _`include/linux/circ_buf.h`:
        https://github.com/torvalds/linux/blob/v3.2/include/linux/circ_buf.h
    '''

    __slots__ = ('_buf', '_head', '_tail', '_consumer_lock', '_producer_lock')

    def __init__(self, buflen=DEFAULT_BUFLEN):
        if buflen & (buflen - 1):
            raise ValueError('buflen must be power of 2')
        self._buf = bytearray(buflen)
        self._head = 0
        self._tail = 0
        self._consumer_lock = threading.Lock()
        self._producer_lock = threading.Lock()

    def __len__(self):
        '''
        :returns: count in buffer
        '''
        head, tail, size = self._head, self._tail, self.buflen
        return (head - tail) & (size - 1)

    @property
    def buflen(self):
        '''
        :returns: buffer length
        '''
        return len(self._buf)

    @property
    def cnt_to_end(self):
        '''
        :returns: count up to the end of the buffer
        '''
        head, tail, size = self._head, self._tail, self.buflen
        end = size - tail
        n = (head + end) & (size - 1)
        return n if n < end else end

    @property
    def space_to_end(self):
        '''
        :returns: space available up to the end of the buffer
        '''
        head, tail, size = self._head, self._tail, self.buflen
        end = size - 1 - head
        n = (end + tail) & (size - 1)
        return n if n <= end else end + 1

    def _produce_mv(self):
        buf, head = self._buf, self._head
        return memoryview(buf)[head: head + self.space_to_end]

    def _consume_mv(self):
        buf, tail = self._buf, self._tail
        return memoryview(buf)[tail:tail + self.cnt_to_end]

    @property
    def producer_buf(self):
        '''
        :returns: producer buffer
        :rtype: :class:`memoryview`
        '''
        def acquire():
            self._producer_lock.acquire()
            return self._produce_mv()

        def release():
            self._producer_lock.release()

        return ResourceManager(acquire, release)

    @property
    def consumer_buf(self):
        '''
        :returns: consumer buffer
        :rtype: :class:`memoryview`
        '''
        def acquire():
            self._consumer_lock.acquire()
            return self._consume_mv()

        def release():
            self._consumer_lock.release()

        return ResourceManager(acquire, release)

    @_require_lock('_producer_lock')
    def produced(self, cnt):
        '''
        :param cnt: written bytes
        :returns: written bytes
        '''
        if cnt > self.space_to_end:
            raise ValueError('cnt bigger than buffer length')
        self._head = (self._head + cnt) & (self.buflen - 1)
        return cnt

    @_require_lock('_consumer_lock')
    def consumed(self, cnt):
        '''
        :param cnt: consumed bytes
        :returns: consumed bytes
        '''
        if cnt > len(self):
            raise ValueError('cnt bigger than buffer length')
        self._tail = (self._tail + cnt) & (self.buflen - 1)
        return cnt

    def __iter__(self):

        def generator():

            def acquire():
                self._consumer_lock.acquire()
                return self._consume_mv()

            def release():
                self._consumer_lock.release()

            while len(self):
                with ResourceManager(acquire, release) as mv:
                    for val in mv:
                        self.consumed(1)
                        yield val

        return generator()


def readinto(buf, readbuf):
    '''
    :param buf: buffer to read into
    :param readbuf: buffer to read from
    :returns: number of bytes read
    '''
    with buf.producer_buf as mv:
        length = min(map(len, (readbuf, mv)))
        if not length:
            return None
        mv[: length] = readbuf[: length]
        buf.produced(length)

    return length
