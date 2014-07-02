from nose import tools
import collections.abc
import functools
import circbuf

def test_init():
    dut = circbuf.CircBuf(128)

    tools.ok_(isinstance(dut, collections.abc.Iterable))
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

    with dut.producer_buf: dut.produced(1)
    dut.consumed(1)


def test_cnt_to_end_space_to_end():
    dut = circbuf.CircBuf(16)

    def produce(n):
        with dut.producer_buf: dut.produced(n)

    def consume(n):
        with dut.consumer_buf: dut.consumed(n)

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
        with dut.producer_buf: dut.produced(n)

    def consume(n):
        with dut.consumer_buf: dut.consumed(n)

    with dut.producer_buf as buf: buf[0] = 42
    produce(1)
    tools.eq_(tuple(dut), (42,))

    with dut.producer_buf as buf:
        length = len(buf)
        buf[:] = bytes(range(1, length + 1))
        dut.produced(length)

    tools.eq_(tuple(dut), tuple(range(1, 16)))


def test_readinto():
    dut = circbuf.CircBuf(16)
    readinto = functools.partial(circbuf.readinto, dut)

    nbytes = readinto(bytes.fromhex('001122'))
    tools.eq_((nbytes, bytes(dut)), (3, bytes.fromhex('001122')))
    tools.eq_(readinto(bytes()), None)
    tools.eq_(*(dut.space_to_end, readinto(bytes(100))))
