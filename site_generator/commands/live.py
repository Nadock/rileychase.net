import asyncio
import functools
import pathlib
from http import server

from watchdog import events, observers

from site_generator import config, errors, logging, pipeline

LOGGER = logging.getLogger()


def live(cfg: config.SiteGeneratorConfig):
    async def _live():
        try:
            await pipeline.pipeline(cfg)
        except Exception as ex:
            errors.log_error(ex)

        pr = PipelineRunner(cfg)

        # Start watching paths for file system events
        observer = observers.Observer()
        observer.schedule(
            pr,
            cfg.pages,
            recursive=True,
        )
        LOGGER.debug(f"Watching {cfg.format_relative_path(cfg.pages)} for file changes")
        observer.schedule(
            pr,
            cfg.templates,
            recursive=True,
        )
        LOGGER.debug(
            f"Watching {cfg.format_relative_path(cfg.templates)} for file changes"
        )
        observer.schedule(
            pr,
            cfg.static,
            recursive=True,
        )
        LOGGER.debug(
            f"Watching {cfg.format_relative_path(cfg.static)} for file changes"
        )

        observer.start()

        # Start serving content
        h = _handler(cfg.output)
        try:
            with server.ThreadingHTTPServer((cfg.host, int(cfg.port)), h) as s:
                LOGGER.info(f"Live server listening at: http://{cfg.host}:{cfg.port}")
                s.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            observer.stop()
            observer.join()

    return _live


def _handler(directory: pathlib.Path):
    return functools.partial(LoggingSimpleHTTPRequestHandler, directory=directory)


class LoggingSimpleHTTPRequestHandler(server.SimpleHTTPRequestHandler):
    def log_message(self, msg: str, *args) -> None:
        LOGGER.info(f"[SERVER] {msg%args}")


class PipelineRunner(events.FileSystemEventHandler):
    def __init__(self, cfg: config.SiteGeneratorConfig):
        super().__init__()
        self._cfg = cfg
        self._lock = asyncio.Lock()

    def on_any_event(self, event):
        asyncio.run(self.run(event))

    async def run(self, event: events.FileSystemEvent):
        LOGGER.info(
            f"File change detected in {self._cfg.format_relative_path(event.src_path)}"
        )
        async with self._lock:
            try:
                await pipeline.pipeline(self._cfg)
            except Exception as ex:
                errors.log_error(ex)
