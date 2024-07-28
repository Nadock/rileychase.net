import asyncio
import datetime
import functools
import time
from collections.abc import Callable
from http import server

from watchdog import events, observers

from site_generator import config, errors, logging, pipeline

LOGGER = logging.getLogger()


def live(cfg: config.SiteGeneratorConfig) -> Callable:
    """Live CLI command handler; build, serve locally, and rebuild site."""

    async def _live() -> None:
        try:
            await pipeline.pipeline(cfg)
        except Exception as ex:
            errors.log_error(ex)

        pipeline_runner = PipelineRunner(cfg)

        # Start watching paths for file system events
        observer = observers.Observer()
        observer.schedule(
            pipeline_runner,
            cfg.pages,
            recursive=True,
        )
        LOGGER.debug(f"Watching {cfg.format_relative_path(cfg.pages)} for file changes")
        observer.schedule(
            pipeline_runner,
            cfg.templates,
            recursive=True,
        )
        LOGGER.debug(
            f"Watching {cfg.format_relative_path(cfg.templates)} for file changes"
        )
        observer.schedule(
            pipeline_runner,
            cfg.static,
            recursive=True,
        )
        LOGGER.debug(
            f"Watching {cfg.format_relative_path(cfg.static)} for file changes"
        )

        observer.start()

        # Start serving content
        handler = functools.partial(
            LoggingSimpleHTTPRequestHandler, directory=str(cfg.output.resolve())
        )
        try:
            with server.ThreadingHTTPServer((cfg.host, int(cfg.port)), handler) as srv:
                LOGGER.info(f"Live server listening at: http://{cfg.host}:{cfg.port}")
                srv.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            observer.stop()
            observer.join()

    return _live


class LoggingSimpleHTTPRequestHandler(server.SimpleHTTPRequestHandler):
    """`SimpleHTTPRequestHandler` with custom logging output."""

    def log_message(self, msg: str, *args: list) -> None:  # noqa: D102
        LOGGER.info(f"[SERVER] {msg%args}")

    def end_headers(self) -> None:  # noqa: D102
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        return super().end_headers()


class PipelineRunner(events.FileSystemEventHandler):
    """
    `watchdog` events handler that reruns the site pipeline on any change.

    The pipeline only runs once within each `window` of time, any additional events
    within that time window are ignored.
    """

    def __init__(
        self,
        cfg: config.SiteGeneratorConfig,
        window: datetime.timedelta = datetime.timedelta(milliseconds=100),
    ) -> None:
        super().__init__()
        self.config = cfg
        self.window = window
        self._lock = asyncio.Lock()
        self._last_run: int = 0

    def on_any_event(self, event: events.FileSystemEvent) -> None:  # noqa: D102
        relative_path = self.config.format_relative_path(event.src_path)
        window_end = self._last_run + int(self.window.total_seconds() * 1_000_000_000)
        now = time.time_ns()

        if window_end >= now:
            LOGGER.info(f"Skipping: {event.event_type}: {relative_path}")
            return

        LOGGER.info(f"Building: {event.event_type}: {relative_path}")
        asyncio.run(self.run_pipeline())
        self._last_run = now

    async def run_pipeline(self) -> None:
        """Run the main `site_generator` pipeline."""
        async with self._lock:
            try:
                await pipeline.pipeline(self.config)
            except Exception as ex:
                errors.log_error(ex)
