# CircBuf

`circbuf.CircBuf` implements a circular buffer for Python.
It allows for zero copy operation, i.e. it uses `memoryview`
to expose consumer and producer buffers.
Access to the buffer is synchronise by locks.

## Example

```Python
import circbuf

buf = circbuf.CircBuf()
# Produce data
with buf.producer_buf as mv:
    mv[0] = 42
    circ_buf.produced(1)

print('First entry: {}'.format(next(buf))) # First entry: 42
```
