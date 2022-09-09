import pathlib
from typing import Callable, Optional

from watchdog import events


def is_outdated(source: Optional[pathlib.Path], dest: Optional[pathlib.Path]) -> bool:
    """
    Compares two files to see if the `dest` file is older than the `source` file.
    """
    if source is None or not source.exists() or not source.is_file():
        return False
    if dest is None or not dest.exists() or not dest.is_file():
        return True
    return source.stat().st_mtime_ns > dest.stat().st_mtime_ns


class FileWatcher(events.FileSystemEventHandler):
    """
    A `watchdog` `FileSystemEventHandler` that forwards the event to a configured callback
    function.

    `callback` must be a callable, if `pass_event` is `True` it must accept at least
    one argument.

    If `pass_event` is `True` the `watchdog` event is passed to the callback function
    as the first argument, otherwise it is not included in the callback.

    `args` and `kwargs` will be passed to the callback function in the normal way.
    """

    def __init__(
        self,
        callback: Callable,
        *,
        pass_event: bool = False,
        args: Optional[list] = None,
        kwargs: Optional[dict] = None,
    ) -> None:
        super().__init__()
        self.pass_event = pass_event
        self.callback = callback
        self.args = args if args else []
        self.kwargs = kwargs if kwargs else {}

    def on_any_event(self, event: events.FileSystemEvent):
        if self.pass_event:
            self.callback(event, *self.args, **self.kwargs)
        else:
            self.callback(*self.args, **self.kwargs)
