import asyncio
import pathlib
from collections.abc import AsyncGenerator
from contextlib import AbstractAsyncContextManager
from types import TracebackType
from typing import Self, TypeVar

from .page import PagePipeline
from .static import StaticPipeline


class WeavingPipeline:
    def __init__(
        self,
        *,
        root: pathlib.Path,
        templates: pathlib.Path,
        output: pathlib.Path,
    ) -> None:
        self._output = output
        self._pl_static = StaticPipeline(root=root, output=output)
        self._pl_pages = PagePipeline(root=root, output=output, templates=templates)

    async def process(
        self, *, static: pathlib.Path, pages: pathlib.Path
    ) -> AsyncGenerator[pathlib.Path | Exception]:
        async for p in yield_as_completed(
            self._pl_pages.process(pages), self._pl_static.process(static)
        ):
            yield p


_T = TypeVar("_T")


class WaitGroup(AbstractAsyncContextManager):
    def __init__(self, count: int = 0) -> None:
        self._count = count
        self._lock = asyncio.Lock()
        self._done = asyncio.Event()

    async def __aenter__(self) -> Self:
        await self.add()
        return self

    async def __aexit__(
        self,
        type: type[BaseException] | None,
        value: BaseException | None,
        tb: TracebackType | None,
    ) -> bool | None:
        await self.remove()
        return None

    async def add(self, delta: int = 1) -> None:
        if delta < 0:
            raise ValueError(f"Delta must be positive, got {delta}")
        async with self._lock:
            self._count += delta
            self._done.clear()

    async def remove(self, delta: int = 1) -> None:
        if delta < 0:
            raise ValueError(f"Delta must be positive, got {delta}")
        async with self._lock:
            self._count = max(self._count - delta, 0)
            if self._count == 0:
                self._done.set()

    async def wait(self) -> None:
        await self._done.wait()

    def done(self) -> bool:
        return self._done.is_set()


async def yield_as_completed(*iters: AsyncGenerator[_T]) -> AsyncGenerator[_T]:
    queue = asyncio.Queue[_T]()
    wg = WaitGroup()

    async def to_queue(i: AsyncGenerator[_T]) -> None:
        async with wg:
            async for p in i:
                await queue.put(p)

    tasks = [asyncio.create_task(to_queue(i)) for i in iters]  # noqa: F841

    while not wg.done() or not queue.empty():
        yield await queue.get()
