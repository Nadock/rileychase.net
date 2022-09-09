from site_generator import config, logging, pipeline

LOGGER = logging.getLogger()


def build(cfg: config.SiteGeneratorConfig):
    """Build CLI command handler; build site once."""

    async def _build():
        await pipeline.pipeline(cfg)

    return _build
