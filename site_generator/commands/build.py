from site_generator import config, pipeline


def build(cfg: config.SiteGeneratorConfig):
    async def _build():
        await pipeline.pipeline(cfg)

    return _build
