import pathlib
import shutil
from collections.abc import AsyncGenerator, Coroutine
from concurrent import futures
from typing import Any

from weaving import errors, log

from .pipeline import Pipeline


class StaticPipeline(Pipeline):
    def __init__(self, *, root: pathlib.Path, output: pathlib.Path) -> None:
        super().__init__(root=root, output=output)
        self.pool_size = 50
        self.log = log.logger("static")

    async def _copy(self, file: pathlib.Path) -> pathlib.Path:
        output = self.get_output(file)

        try:
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(file, output)
        except Exception as ex:
            raise errors.WeavingError(
                f"Copying static file from {file.relative_to(self.root)} to "
                f"{output.relative_to(self.output)} failed: {ex}"
            ) from ex

        self.log.debug(
            f"Copied {file.relative_to(self.root.parent)} to "
            f"{output.relative_to(self.output.parent)}"
        )

        return output

    async def process(
        self, static: pathlib.Path
    ) -> AsyncGenerator[pathlib.Path | Exception]:
        _futures: list[futures.Future[Coroutine[Any, Any, pathlib.Path]]] = []
        with futures.ThreadPoolExecutor(self.pool_size) as pool:
            for path, _, files in static.walk():
                _futures.extend([pool.submit(self._copy, path / f) for f in files])

            for fut in futures.as_completed(_futures):
                try:
                    yield await fut.result()
                except Exception as ex:
                    yield ex
