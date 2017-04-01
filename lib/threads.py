import sublime
import threading

###----------------------------------------------------------------------------


def _spinner_key():
    """
    Get a unique Sublime status key in a thread safe way.
    """
    with _spinner_key.lock:
        _spinner_key.counter += 1
        return "_spinner_%d" % _spinner_key.counter

_spinner_key.counter = 0
_spinner_key.lock = threading.Lock()


###----------------------------------------------------------------------------

class Spinner():
    """
    A simple spinner that follows the active view in the provided window which
    self terminates when the provided thread is no longer running.

    The spinner is prefixed with the given prefix text so you can tell what
    it is for.
    """
    spin_text = "|/-\\"

    def __init__(self, window, thread, prefix):
        self.window = window
        self.thread = thread
        self.prefix = prefix
        self.key = _spinner_key()
        self.tick_view = None

        sublime.set_timeout(lambda: self.tick(0), 250)

    def tick(self, position):
        current_view = self.window.active_view()

        if self.tick_view is not None and current_view != self.tick_view:
            self.tick_view.erase_status(self.key)
            self.tick_view = None

        if not self.thread.is_alive():
            current_view.erase_status(self.key)
            return

        text = "%s [%s]" % (self.prefix, self.spin_text[position])
        position = (position + 1) % len(self.spin_text)

        current_view.set_status(self.key, text)
        if self.tick_view is None:
            self.tick_view = current_view

        sublime.set_timeout(lambda: self.tick(position), 250)


###----------------------------------------------------------------------------


class BackgroundWorkerThread(threading.Thread):
    """
    A thread for performing a task in the background, optionally executing a
    callback in the main thread when processing has completed.

    If given, the callback is invoked in the main thread after processing has
    completed, with the thread instance as a parameter so that results can be
    collected.
    """
    def __init__(self, window, spinner_text, callback, **kwargs):
        super().__init__()

        self.window = window
        self.spinner_text = spinner_text
        self.callback = callback
        self.args = kwargs

    def _process(self):
        pass

    def run(self):
        Spinner(self.window, self, self.spinner_text)

        self._process()

        if self.callback is not None:
            # Make sure we don't make a circular reference to ourselves or we
            # will leak when the thread terminates.
            callback = self.callback
            del self.callback

            sublime.set_timeout(lambda: callback(self), 1)


###----------------------------------------------------------------------------
