import dataclasses
from typing import Annotated

import cyclopts

from weaving import log, new, types

from . import cli

app = cyclopts.App("new", help="Create blank pages, templates, or blog posts.")
cli.app.command(app)


@cyclopts.Parameter(name="*", group="Frontmatter")
@dataclasses.dataclass()
class Frontmatter:
    """Common frontmatter parameters as a group."""

    debug: bool | None = None
    """Set the frontmatter `debug` property to `true`."""

    template: str | None = None
    """Set the frontmatter `template` property."""

    title: str | None = None
    """Set the frontmatter `title` property."""

    subtitle: str | None = None
    """Set the frontmatter `subtitle` property."""

    description: str | None = None
    """Set the frontmatter `description` property."""


@cyclopts.Parameter(name="*")
@dataclasses.dataclass()
class _NewParameters:
    name: Annotated[
        str,
        cyclopts.Parameter(
            help=(
                "The name of the new resource. Any `/` characters will be treated as "
                "directory separators and the appropriate file extension will be added "
                "if not set."
            )
        ),
    ]


@app.command()
async def template(
    params: _NewParameters, /, *, site: cli.SiteConfig | None = None
) -> None:
    """Create a site template."""
    site = site or cli.SiteConfig()

    if not params.name.endswith(".html"):
        params.name += ".html"
    path = await new.new_html(site.templates / params.name)

    log.logger().info(f"New template created at {path.relative_to(site.root)}")


@app.command()
async def page(
    params: _NewParameters,
    /,
    *,
    frontmatter: Frontmatter | None = None,
    site: cli.SiteConfig | None = None,
) -> None:
    """Create a site page."""
    site = site or cli.SiteConfig()
    frontmatter = frontmatter or Frontmatter()

    fm = types.PageFrontmatter(
        type="default",
        title=frontmatter.title,
        subtitle=frontmatter.subtitle,
        description=frontmatter.description,
    )
    if frontmatter.debug is not None:
        fm.debug = frontmatter.debug
    if frontmatter.template is not None:
        fm.template = frontmatter.template

    if not params.name.endswith(".md"):
        params.name += ".md"
    path = await new.new_markdown(site.pages / params.name, fm)

    log.logger().info(f"New page created at {path.relative_to(site.root)}")


@app.command()
async def post(
    params: _NewParameters,
    /,
    *,
    frontmatter: Frontmatter | None = None,
    site: cli.SiteConfig | None = None,
) -> None:
    """Create a blog post."""
    site = site or cli.SiteConfig()
    frontmatter = frontmatter or Frontmatter()

    fm = types.PageFrontmatter(
        type="blog_post",
        title=frontmatter.title,
        subtitle=frontmatter.subtitle,
        description=frontmatter.description,
    )
    if frontmatter.debug is not None:
        fm.debug = frontmatter.debug
    if frontmatter.template is not None:
        fm.template = frontmatter.template

    if not params.name.endswith(".md"):
        params.name += ".md"
    path = await new.new_markdown(site.pages / "blog" / params.name, fm)

    log.logger().info(f"New blog post created at {path.relative_to(site.root)}")
