import abc
import pathlib
from collections.abc import AsyncGenerator


class Pipeline(abc.ABC):
    def __init__(self, *, root: pathlib.Path, output: pathlib.Path) -> None:
        super().__init__()
        self.root = root
        self.output = output

    def get_output(self, file: pathlib.Path) -> pathlib.Path:
        return self.output / (file.relative_to(self.root))

    def process(self, _: pathlib.Path) -> AsyncGenerator[pathlib.Path | Exception]:
        raise NotImplementedError
