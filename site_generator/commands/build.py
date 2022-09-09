from site_generator import config, errors, logging, pipeline

LOGGER = logging.getLogger()


def build(cfg: config.SiteGeneratorConfig):
    async def _build():
        try:
            await pipeline.pipeline(cfg)
        except Exception as ex:
            errors.log_error(ex)

    return _build
