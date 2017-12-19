from Queue import Queue, Empty
from threading import Thread


class NonBlockingStreamReader(object):
    def __init__(self, stream):
        """
        stream: the stream to read from.
                Usually a process' stdout or stderr.
        """

        self._s = stream
        self._q = Queue()

        def _handle_enqueued_data(stream, queue):
            """
            Collect lines from 'stream' and put them in 'queue'.
            """

            while True:
                line = stream.readline()
                if line:
                    queue.put(line)
                else:
                    # Stop Iteration
                    return

        self._t = Thread(target=_handle_enqueued_data,
                         args=(self._s, self._q))
        self._t.daemon = True
        self._t.start()  # start collecting lines from the stream

    def read_line(self, timeout=None):
        """
        Performs reading on buffer.
        :param timeout:
        :return: Enqueued data or None if an exception occurs
        """
        try:
            return self._q.get(block=timeout is not None,
                               timeout=timeout)
        except Empty:
            return None
