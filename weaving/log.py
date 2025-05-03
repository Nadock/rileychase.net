import asyncio
import logging

import cyclopts
import jinja2
from rich import logging as rich_logging


def configure(*, verbose: bool) -> None:
    """
    Configure logging output from `weaving` CLI.

    Must be called before attempting to log anything, or the log lines will be lost.
    """
    logging.basicConfig(
        level="ERROR",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            rich_logging.RichHandler(
                show_time=True,
                show_level=True,
                markup=True,
                rich_tracebacks=True,
                show_path=False,
                tracebacks_suppress=[cyclopts, asyncio, jinja2],
            )
        ],
    )

    log = logging.getLogger().getChild("weaving")
    if verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)


def logger(name: str | None = None) -> logging.Logger:
    """Get a `logging.Logger` instance."""
    log = logging.getLogger("weaving")
    if name:
        return log.getChild(name)
    return log
