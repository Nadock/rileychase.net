import asyncio

from site_generator import config, markdown, static


async def pipeline(cfg: config.SiteGeneratorConfig):
    coros = []
    async for page in markdown.find_markdown(cfg.pages):
        coros.append(markdown.markdown_pipeline(cfg, page))
    async for file in static.find_static(cfg.static):
        coros.append(static.static_pipeline(cfg, file))
    await asyncio.gather(*coros)
