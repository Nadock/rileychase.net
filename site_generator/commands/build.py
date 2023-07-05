from collections.abc import Callable

from site_generator import config, logging, pipeline

LOGGER = logging.getLogger()


def build(cfg: config.SiteGeneratorConfig) -> Callable:
    """Build CLI command handler; build site once."""

    async def _build() -> None:
        await pipeline.pipeline(cfg)

    return _build
