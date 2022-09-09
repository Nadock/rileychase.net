import asyncio
import functools
from http import server

from watchdog import events, observers  # type: ignore

from site_generator import config, errors, logging, pipeline

LOGGER = logging.getLogger()


def live(cfg: config.SiteGeneratorConfig):
    """Live CLI command handler; build, serve locally, and rebuild site."""

    async def _live():
        try:
            await pipeline.pipeline(cfg)
        except Exception as ex:  # pylint: disable=broad-except
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
            LoggingSimpleHTTPRequestHandler, directory=cfg.output
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

    def log_message(self, msg: str, *args) -> None:
        # pylint: disable=arguments-differ
        LOGGER.info(f"[SERVER] {msg%args}")


class PipelineRunner(events.FileSystemEventHandler):
    """
    `watchdog` events handler that reruns the site pipeline on any change.

    Additionally, `PipelineRunner` ensures that only one pipeline is running per
    instance of this class.
    """

    def __init__(self, cfg: config.SiteGeneratorConfig):
        super().__init__()
        self._cfg = cfg
        self._lock = asyncio.Lock()

    def on_any_event(self, event):
        asyncio.run(self.run(event))

    async def run(self, event: events.FileSystemEvent):
        """Run the main `site_generator` pipeline."""
        LOGGER.info(
            f"File change detected in {self._cfg.format_relative_path(event.src_path)}"
        )
        async with self._lock:
            try:
                await pipeline.pipeline(self._cfg)
            except Exception as ex:  # pylint: disable=broad-except
                errors.log_error(ex)
