import asyncio
import pathlib

from .markdown import PagePipeline
from .static import StaticPipeline


class WeavingPipeline:
    def __init__(
        self,
        *,
        root: pathlib.Path,
        templates: pathlib.Path,
        output: pathlib.Path,
        static: pathlib.Path,
        pages: pathlib.Path,
    ) -> None:
        self._static_pipeline = StaticPipeline(root=root, output=output)
        self._static = static

        self._page_pipeline = PagePipeline(
            root=root, output=output, templates=templates
        )
        self._pages = pages

    async def process(self) -> None:
        # TODO(Nadock): delete existing build output before regenerating
        await asyncio.gather(
            self._process_static(self._static), self._process_pages(self._pages)
        )

    async def _process_pages(self, path: pathlib.Path) -> None:
        if path.is_file():
            await self._page_pipeline.process(path)
            return

        await asyncio.gather(*[self._process_pages(p) for p in path.iterdir()])
        await self._page_pipeline.finalise()

    async def _process_static(self, path: pathlib.Path) -> None:
        if path.is_file():
            await self._static_pipeline.process(path)
            return

        await asyncio.gather(*[self._process_static(p) for p in path.iterdir()])
        await self._static_pipeline.finalise()
