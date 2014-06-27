# CircBuf

`circbuf.CircularBuffer` implements a circular buffer for Python.
It aims to be copy less, i.e. it uses `memoryview` to expose consumer and
producer buffers. Access to the buffer is synchronise by locks.

```Python
import circbuf

circ_buf = circbuf.CircularBuffer()
# Produce data
with circ_buf.producer_buffer as mv:
    mv[0] = 42
    circ_buf.produced(1)

print('First entry: {}'.format(next(circ_buf))) # First entry: 42
```
