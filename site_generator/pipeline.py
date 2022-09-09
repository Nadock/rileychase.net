import asyncio

from site_generator import config, markdown, static


async def pipeline(cfg: config.SiteGeneratorConfig):
    tasks = []
    async for page in markdown.find_markdown(cfg.pages):
        tasks.append(markdown.markdown_pipeline(cfg, page))
    async for file in static.find_static(cfg.static):
        tasks.append(static.static_pipeline(cfg, file))
    await asyncio.gather(*tasks)
