import asyncio
import functools
from http import server

from watchdog import events, observers

from site_generator import config, logging, pipeline

LOGGER = logging.getLogger()


def live(cfg: config.SiteGeneratorConfig):
    async def _live():
        LOGGER.info("Building site")
        await pipeline.pipeline(cfg)
        LOGGER.debug("First time build complete")

        pr = PipelineRunner(cfg)

        # Start watching paths for file system events
        observer = observers.Observer()
        observer.schedule(
            pr,
            cfg.pages,
            recursive=True,
        )
        observer.schedule(
            pr,
            cfg.templates,
            recursive=True,
        )
        observer.schedule(
            pr,
            cfg.static,
            recursive=True,
        )
        observer.start()
        LOGGER.debug("File system watcher started")

        # Start serving content
        h = functools.partial(server.SimpleHTTPRequestHandler, directory=cfg.output)
        try:
            with server.ThreadingHTTPServer((cfg.host, int(cfg.port)), h) as s:
                LOGGER.info(f"Starting dev server at http://{cfg.host}:{cfg.port}")
                s.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            observer.stop()
            observer.join()

    return _live


class PipelineRunner(events.FileSystemEventHandler):
    def __init__(self, cfg: config.SiteGeneratorConfig):
        super().__init__()
        self._cfg = cfg
        self._lock = asyncio.Lock()

    def on_any_event(self, event):
        asyncio.run(self.run(event))

    async def run(self, event: events.FileSystemEvent):
        LOGGER.info(f"{event.src_path} changed, rebuilding site")
        async with self._lock:
            LOGGER.debug(f"{self.__class__.__name__}.run2 => lock acquired")
            await pipeline.pipeline(self._cfg)
        LOGGER.info("Site rebuilt")
