import asyncio
import shutil
import time

from site_generator import config, errors, logging, markdown, static

LOGGER = logging.getLogger()


async def pipeline(cfg: config.SiteGeneratorConfig) -> None:
    """Generate the entire site once end-to-end."""
    time_st = time.time_ns()
    try:
        shutil.rmtree(cfg.output)
        LOGGER.debug(f"{cfg.format_relative_path(cfg.output)} cleared")
    except Exception as ex:
        raise errors.PipelineError(
            f"Cannot clear output directory {cfg.format_relative_path(cfg.output)}: "
            f"{ex}"
        ) from ex

    tasks = []
    async for page in markdown.find_markdown(cfg.pages):
        tasks.append(markdown.markdown_pipeline(cfg, page))  # noqa: PERF401

    async for file in static.find_static(cfg.static):
        tasks.append(static.static_pipeline(cfg, file))  # noqa: PERF401

    await asyncio.gather(*tasks)
    time_en = time.time_ns()

    LOGGER.info(
        f"Site build complete in {(time_en - time_st) / 1_000_000:.3f}ms, "
        f"contents written to {cfg.format_relative_path(cfg.output)}"
    )
