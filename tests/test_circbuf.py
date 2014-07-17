from nose import tools
import sys
IS_PY32 = sys.version_info < (3, 3)
if IS_PY32:
    import mock
    from collections import Iterable
else:
    from unittest import mock
    from collections.abc import Iterable
import functools
import circbuf


def test_resource_manger_acquire_release():
    acquire = mock.Mock(return_value=42)
    release = mock.Mock()
    dut = circbuf.ResourceManager(acquire, release)

    with dut as res:
        tools.eq_(res, 42)
        tools.eq_(acquire.call_count, 1)
        tools.eq_(release.call_count, 0)
    tools.eq_(acquire.call_count, 1)
    tools.eq_(release.call_count, 1)


def test_resource_manager_check_ok():
    acquire = mock.Mock(return_value=42)
    release = mock.Mock()
    check = mock.Mock(return_value=True)
    dut = circbuf.ResourceManager(acquire, release, check)

    with dut:
        tools.eq_(check.call_count, 1)
        tools.eq_(check.call_args, ((42,),))


@tools.raises(RuntimeError)
def test_resource_manger_check_nok():
    acquire = mock.Mock()
    release = mock.Mock()
    check = mock.Mock(return_value=False)
    dut = circbuf.ResourceManager(acquire, release, check)

    with dut:
        pass


def test_init():
    dut = circbuf.CircBuf(128)

    tools.ok_(isinstance(dut, Iterable))
    tools.eq_(len(dut), 0)
    tools.eq_(dut.buflen, 128)


@tools.raises(ValueError)
def test_init_raises_if_not_pwr_of_two():
    circbuf.CircBuf(15)


@tools.raises(RuntimeError)
def test_produced_requires_lock():
    dut = circbuf.CircBuf()

    dut.produced(1)


@tools.raises(RuntimeError)
def test_consumed_requires_lock():
    dut = circbuf.CircBuf()

    with dut.producer_buf:
        dut.produced(1)
    dut.consumed(1)


def test_cnt_to_end_space_to_end():
    dut = circbuf.CircBuf(16)

    def produce(n):
        with dut.producer_buf:
            dut.produced(n)

    def consume(n):
        with dut.consumer_buf:
            dut.consumed(n)

    tools.eq_((dut.cnt_to_end, dut.space_to_end), (0, dut.buflen - 1))
    produce(dut.buflen - 1)
    tools.eq_((dut.cnt_to_end, dut.space_to_end), (dut.buflen - 1, 0))
    consume(dut.buflen - 1)
    tools.eq_((dut.cnt_to_end, dut.space_to_end), (0, 1))
    produce(1)
    tools.eq_((dut.cnt_to_end, dut.space_to_end), (1, dut.buflen - 2))
    consume(1)
    tools.eq_((dut.cnt_to_end, dut.space_to_end), (0, dut.buflen - 1))


def test_iterator():
    dut = circbuf.CircBuf(16)

    def produce(n):
        with dut.producer_buf:
            dut.produced(n)

    def consume(n):
        with dut.consumer_buf:
            dut.consumed(n)

    with dut.producer_buf as buf:
        if IS_PY32:
            buf[0] = bytes((42,))
        else:
            buf[0] = 42
    produce(1)
    tools.eq_(tuple(dut), (42,))

    with dut.producer_buf as buf:
        length = len(buf)
        buf[:] = bytes(range(1, length + 1))
        dut.produced(length)

    tools.eq_(tuple(dut), tuple(range(1, 16)))


def test_iterator_wrap_around():
    dut = circbuf.CircBuf(16)

    with dut.producer_buf:
        dut.produced(5)
    tools.eq_(len(dut), 5)
    # fill buffer
    with dut.producer_buf as buf:
        dut.produced(len(buf))
    with dut.producer_buf as buf:
        dut.produced(len(buf))
    # test wrap around
    tools.eq_(len(dut), 15, 'shall wrap around')


def test_space_avail():
    buf = circbuf.CircBuf(16)
    dut = circbuf.space_avail

    def produce(n):
        with buf.producer_buf:
            buf.produced(n)

    def consume(n):
        with buf.consumer_buf:
            buf.consumed(n)

    tools.eq_(dut(buf), 15)
    produce(1)
    tools.eq_(dut(buf), 14)
    consume(1)
    tools.eq_(dut(buf), 15)


@tools.raises(ValueError)
def test_released_producer_buf():
    buf = circbuf.CircBuf()
    dut = None

    with buf.producer_buf as mv:
        dut = mv
    dut[0]


@tools.raises(ValueError)
def test_released_consumer_buf():
    buf = circbuf.CircBuf()
    dut = None

    with buf.consumer_buf as mv:
        dut = mv
    dut[0]


def test_readinto_exported():
    tools.ok_('readinto' in circbuf.__all__)


def test_readinto():
    buf = circbuf.CircBuf(16)
    dut = functools.partial(circbuf.readinto, buf)

    nbytes = dut(bytes.fromhex('001122'))
    tools.eq_((nbytes, bytes(buf)), (3, bytes.fromhex('001122')))
    tools.eq_(dut(bytes()), None)
    tools.eq_(*(circbuf.space_avail(buf), dut(bytes(100))))


def test_recv_is_exported():
    tools.ok_('recv' in circbuf.__all__)


def test_recv():
    buf = circbuf.CircBuf()
    dut = functools.partial(circbuf.recv, buf)
    recv = mock.Mock(return_value=42)

    dut(recv)
    tools.eq_(recv.call_count, 1)
    tools.eq_(len(buf), 42)

    recv.reset_mock()
    dut(recv, 'arg')
    tools.eq_(recv.call_count, 1)
    tools.eq_(recv.call_args[0][-1], 'arg')


def test_seek_to_pattern_is_exported():
    tools.ok_('seek_to_pattern' in circbuf.__all__)


def test_seek_to_pattern():
    buf = circbuf.CircBuf()
    dut = functools.partial(circbuf.seek_to_pattern, buf)

    circbuf.readinto(buf, bytes.fromhex('11 22 2a 01 02'))
    tools.eq_(dut(42), 2)
    tools.eq_(tuple(buf), (1, 2))

    circbuf.readinto(buf, bytes.fromhex('11 22 2a 01 02'))
    tools.eq_(dut(bytes.fromhex('2a 01')), 1)
    tools.eq_(tuple(buf), (2,))
    tools.eq_(dut(42), 0)
