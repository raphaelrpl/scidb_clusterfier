from Queue import Queue, Empty
from threading import Thread, Event


class StreamReaderThread(Thread):
    def __init__(self, stream, resource):
        super(StreamReaderThread, self).__init__()
        self._stop_event = Event()
        self._stream = stream
        self._resource = resource

    def stop(self):
        self._stop_event.set()

    def is_stopped(self):
        return self._stop_event.is_set()

    def run(self):
        """
        Collect lines output from 'stream' and put them in 'queue'.
        """

        while not self.is_stopped() and not self._stream.closed:
            line = self._stream.readline()
            if line:
                self._resource.put(line)


class NonBlockingStreamReader(object):
    def __init__(self, stream):
        """
        :param stream: the stream to read from. Usually a process' stdout or stderr.
        """

        self._s = stream
        self._q = Queue()

        self._t = StreamReaderThread(stream, self._q)
        # self._t.daemon = True
        self._t.start()  # start collecting lines from the stream

    def read_line(self, timeout=None):
        """
        Performs reading on buffer.
        :param timeout:
        :return: Enqueued data or None if an exception occurs
        """
        try:
            res = self._q.get(block=timeout is not None,
                              timeout=timeout)
            return res
        except Empty:
            return None

    def close(self):
        if not self._s.closed:
            self._t.stop()
        self._t.join()


def is_array(elm):
    return isinstance(elm, list) or isinstance(elm, tuple)


def is_string(value):
    return isinstance(value, basestring)


def is_int(value):
    return isinstance(value, int)


def is_string_present_in(key, obj):
    return key in obj and is_string(obj[key])


def is_int_present_in(key, obj):
    return key in obj and is_int(obj[key])