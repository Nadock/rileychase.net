import os
import pathlib
import shutil
from collections.abc import AsyncIterator

from site_generator import config, errors, logging

LOGGER = logging.getLogger()


async def static_pipeline(
    cfg: config.SiteGeneratorConfig, path: pathlib.Path
) -> pathlib.Path:
    """
    Process a static file by copying it into the same relative location in the output
    directory.
    """
    try:
        output = (cfg.output / path.relative_to(cfg.static)).absolute()
    except Exception as ex:
        raise errors.PipelineError(
            f"Cannot compute output location for static file "
            f"{cfg.format_relative_path(path)}: {ex}"
        ) from ex

    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output = shutil.copy(path, output)
    except Exception as ex:
        raise errors.PipelineError(
            f"Unable to write static file {cfg.format_relative_path(path)} to output: "
            f"{ex}"
        ) from ex

    LOGGER.debug(
        f"Static pipeline converted {cfg.format_relative_path(path)} "
        f"to {cfg.format_relative_path(output)}"
    )
    return output


async def find_static(path: pathlib.Path) -> AsyncIterator[pathlib.Path]:
    """Find any files static files under a root `path`."""
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            yield pathlib.Path(dirpath) / filename
