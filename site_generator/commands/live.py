import asyncio
import functools
from http import server

from watchdog import observers

from site_generator import config, file_util, markdown, pipeline_manager, static


def live(cfg: config.SiteGeneratorConfig):
    async def _live():
        print(f"live! {cfg.host=}, {cfg.port=}")

        init_tasks = []

        observer = observers.Observer()
        with pipeline_manager.PipelineManager(cfg) as mgr:
            async for path in markdown.find_markdown(cfg.pages):
                # Add initial build to init tasks
                init_tasks.append(
                    asyncio.create_task(markdown.markdown_pipeline(cfg, path))
                )
                # Setup watcher for this path to trigger rebuilds
                observer.schedule(
                    file_util.FileWatcher(mgr.enqueue, args=[path, "markdown"]), path
                )

            async for path in static.find_static(cfg.pages):
                # Add initial build to init tasks
                init_tasks.append(
                    asyncio.create_task(static.static_pipeline(cfg, path))
                )
                # Setup watcher for this path to trigger rebuilds
                observer.schedule(
                    file_util.FileWatcher(mgr.enqueue, args=[path, "static"]), path
                )

            # Finish all init tasks before continuing
            asyncio.gather(*init_tasks)

            # Start watching paths for file system events
            observer.start()

            # Start serving content
            web_handler = functools.partial(
                server.SimpleHTTPRequestHandler, directory=cfg.output
            )
            with server.ThreadingHTTPServer(
                (cfg.host, int(cfg.port)), web_handler
            ) as web_server:
                web_server.serve_forever()

    return _live
