import functools
from http import server

from site_generator import config, pipeline


def live(cfg: config.SiteGeneratorConfig):
    async def _live():
        print(f"live! {cfg.host=}, {cfg.port=}")

        await pipeline.pipeline(cfg)

        web_handler = functools.partial(
            server.SimpleHTTPRequestHandler, directory=cfg.output
        )
        with server.ThreadingHTTPServer(
            (cfg.host, int(cfg.port)), web_handler
        ) as web_server:
            web_server.serve_forever()

    return _live
