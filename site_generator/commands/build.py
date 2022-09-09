import asyncio

from site_generator import config, logging, markdown, pipeline, static

LOGGER = logging.getLogger()


def build(cfg: config.SiteGeneratorConfig):
    async def _build():
        await pipeline.pipeline(cfg)
        LOGGER.info(f"Site build complete, contents written to {cfg.output}")

    return _build
