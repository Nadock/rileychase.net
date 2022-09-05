import os
import pathlib
import shutil
from typing import AsyncIterator

from . import config


async def static_pipeline(
    cfg: config.SiteGeneratorConfig, source: pathlib.Path
) -> pathlib.Path:
    """
    Process a static file by copying it into the same relative location in the output
    directory.
    """
    output = (cfg.output / cfg.static.relative_to(source)).absolute()
    output.parent.mkdir(parents=True, exist_ok=True)
    return shutil.copy(source, output)


async def find_static(path: pathlib.Path) -> AsyncIterator[pathlib.Path]:
    """Find any files static files under a root `path`."""
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            yield pathlib.Path(dirpath) / filename
