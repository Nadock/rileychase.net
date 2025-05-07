import dataclasses
import logging
import pathlib
import shutil
from typing import Annotated, Any

import cyclopts
import rich
import rich.logging
import rich.traceback
from cyclopts.types import Directory

from weaving import log, pipeline

app = cyclopts.App(name="weaving")


@app.meta.default
def launcher(
    *tokens: Annotated[str, cyclopts.Parameter(show=False, allow_leading_hyphen=True)],
    verbose: Annotated[
        bool,
        cyclopts.Parameter(
            negative=(), help="Print verbose output details.", group="Commands"
        ),
    ] = False,
) -> Any:
    """Custom launcher for root `weaving` `cyclopts.App`."""
    log.configure(verbose=verbose)
    return app(tokens)


@cyclopts.Parameter(name="*", group="Site config")
@dataclasses.dataclass()
class SiteConfig:
    """Common site config parameters as a group."""

    pages: Directory = pathlib.Path("pages")
    """Source directory for site pages."""

    templates: Directory = pathlib.Path("templates")
    """Source directory for page templates."""

    static: Directory = pathlib.Path("static")
    """Source directory for site static files."""

    root: cyclopts.types.Directory = pathlib.Path()
    """Common root directory for site contents."""

    def __post_init__(self) -> None:
        self.pages = self.pages.resolve()
        self.templates = self.templates.resolve()
        self.static = self.static.resolve()
        self.root = self.root.resolve()


@cyclopts.Parameter(name="*", group="Opengraph")
@dataclasses.dataclass()
class _OpengraphConfig:
    og_name: str | None = None
    """Site name for OpenGraph tags."""
    og_local: str | None = None
    """Site local for OpenGraph tags."""


@app.command()
async def build(
    site: SiteConfig | None = None,
    open_graph: _OpengraphConfig | None = None,
    debug_pages: Annotated[bool, cyclopts.Parameter(negative=())] = False,
    output: Directory = pathlib.Path("./output"),
) -> None:
    """
    Build the site.

    Parameters
    ----------
    debug_pages:
        Include debug pages in site build output.

    output:
        The path for the output of the site generation.
    """
    site = site or SiteConfig()

    if output.exists():
        log.logger().debug(f"deleting old build in {output}")
        shutil.rmtree(output)

    pl = pipeline.WeavingPipeline(
        root=site.root,
        templates=site.templates,
        output=output,
    )

    async for p_or_e in pl.process(static=site.static, pages=site.pages):
        if isinstance(p_or_e, Exception):
            log.logger().error(p_or_e)
            log_template_errors(site.templates, p_or_e)


def log_template_errors(templates: pathlib.Path, ex: BaseException | None) -> None:
    # Exit quickly if the logger is not enabled
    if not log.logger().isEnabledFor(logging.DEBUG):
        return

    # Walk up exception chain to print any template errors
    while ex:
        if _log_template_exception(templates, ex):
            return
        ex = ex.__cause__


def _log_template_exception(templates: pathlib.Path, ex: BaseException) -> bool:
    # Convert exception to rich traceback
    rtb = rich.traceback.Traceback(
        rich.traceback.Traceback.extract(type(ex), ex, ex.__traceback__)
    )

    # Drop any frames that are not from template files
    has_template_frames = False
    for stack in rtb.trace.stacks:
        frames = []
        for frame in stack.frames:
            path = pathlib.Path(frame.filename)
            if path.is_relative_to(templates):
                has_template_frames = True
                frames.append(frame)
        stack.frames = frames

    if not has_template_frames:
        return False

    # Find a rich.logging.RichHandler
    handler: rich.logging.RichHandler | None = None
    logger: logging.Logger | None = log.logger()
    while logger:
        for h in logger.handlers:
            if isinstance(h, rich.logging.RichHandler):
                handler = h
                break
        logger = logger.parent
    if not handler:
        return False

    # Manually print the traceback
    handler.console.print(
        handler.render(
            record=logging.LogRecord(
                name="",
                level=logging.DEBUG,
                pathname="",
                lineno=0,
                msg="",
                args=None,
                exc_info=None,
            ),
            message_renderable=rtb,
            traceback=None,
        )
    )
    return True
