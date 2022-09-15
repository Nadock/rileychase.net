import asyncio
import shutil

from site_generator import config, errors, logging, markdown, static

LOGGER = logging.getLogger()


async def pipeline(cfg: config.SiteGeneratorConfig):
    """Generate the entire site once end-to-end."""
    try:
        shutil.rmtree(cfg.output)
        LOGGER.debug(f"{cfg.format_relative_path(cfg.output)} cleared")
    except Exception as ex:
        raise errors.PipelineError(
            f"Cannot clear output directory {cfg.format_relative_path(cfg.output)}: {ex}"
        )

    tasks = []
    async for page in markdown.find_markdown(cfg.pages):
        tasks.append(markdown.markdown_pipeline(cfg, page))

    async for file in static.find_static(cfg.static):
        tasks.append(static.static_pipeline(cfg, file))

    await asyncio.gather(*tasks)

    LOGGER.info(
        f"Site build complete, contents written to {cfg.format_relative_path(cfg.output)}"
    )
