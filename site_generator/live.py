import asyncio
import contextlib
import importlib
import pathlib
import subprocess
import sys
from collections.abc import Callable, Coroutine

import watchfiles

from site_generator import config, logging, pipeline

LOGGER = logging.getLogger()


async def watch_and_serve(cfg: config.SiteGeneratorConfig) -> None:
    """Watch for file changes and serve the live site."""
    await asyncio.gather(_watch_site_files(cfg), _serve_live_site(cfg))


async def _watch_site_files(cfg: config.SiteGeneratorConfig) -> None:
    paths = [cfg.templates, cfg.pages, cfg.static]
    LOGGER.debug(f"Watching {paths} for site changes")
    await watchfiles.arun_process(
        *paths, target=_run_process_callback, args=(pipeline.pipeline, cfg)
    )


def _run_process_callback(
    cr: Callable[[config.SiteGeneratorConfig], Coroutine[None, None, None]],
    cfg: config.SiteGeneratorConfig,
) -> None:
    with contextlib.suppress(KeyboardInterrupt):
        logging.configure_logging(cfg)
        asyncio.run(cr(cfg))


async def _serve_live_site(cfg: config.SiteGeneratorConfig) -> None:
    adev_module = importlib.import_module("aiohttp_devtools")

    if not adev_module.__file__:
        raise RuntimeError("Error locating adev binary")

    adev = (
        pathlib.Path(adev_module.__file__)
        / ".."
        / ".."
        / ".."
        / ".."
        / ".."
        / "bin"
        / "adev"
    )

    proc = await asyncio.create_subprocess_exec(
        adev.resolve(),
        "serve",
        "--livereload",
        "--no-browser-cache",
        "--port",
        str(cfg.port),
        cfg.output.resolve(),
        stdout=sys.stderr,
        stderr=sys.stderr,
    )

    try:
        code = await proc.wait()
    except subprocess.SubprocessError as ex:
        raise RuntimeError("Error while running dev server subprocess") from ex
    except Exception:  # noqa: S110
        pass
    finally:
        with contextlib.suppress(Exception):
            proc.kill()

    if code != 0:
        raise RuntimeError(f"Dev server subprocess exited early with exit code {code}")
