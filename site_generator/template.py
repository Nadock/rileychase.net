import datetime
import pathlib
import re
from typing import Any

import jinja2
import pydantic

from site_generator import frontmatter, logging

LOGGER = logging.getLogger()


class TemplateContext(pydantic.BaseModel):
    """Template context for rendering `default` type pages."""

    content: str
    """Pre-rendered page content as HTML."""

    frontmatter: frontmatter.PageFrontmatter
    """Page frontmatter."""

    rendered_at: datetime.datetime
    """The date and time the page is being rendered at."""

    modified_at: datetime.datetime
    """The date and time the page source was last modified."""

    git_sha: str | None
    """The git SHA of the current HEAD commit during the build process."""


class BlogIndexPostContext(pydantic.BaseModel):
    """Template context for blog posts on a blog index."""

    frontmatter: frontmatter.PageFrontmatter
    """Page frontmatter for the blog post."""

    preview: str
    """Blog post preview."""


class BlogIndexTemplateContext(TemplateContext):
    """Template context for rendering `blog_index` type pages."""

    posts: list[BlogIndexPostContext]
    """The blog posts to include in the blog index page."""

    current_page: int
    """The page number for the blog index page being rendered."""

    max_pages: int
    """The maximum number of blog index pages to be rendered."""


class TemplateRenderer:
    """Render templates in a persistent Jinja environment."""

    def __init__(self, templates: pathlib.Path) -> None:
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(templates),
            autoescape=True,
            enable_async=True,
        )
        self.env.filters["render"] = _render_filter

    async def render(self, names: list[str], ctx: TemplateContext) -> str:
        """Render the named template with the provided render context."""
        template = self.env.get_or_select_template([n for n in names if n])

        try:
            html = await template.render_async(ctx=ctx)
        except jinja2.TemplateError as ex:
            if (
                ex.message
                and (match := re.match(r"'(?P<field>.+)' is undefined", ex.message))
                and (field := match.group("field"))
            ):
                ex.args = (f'Unknown template context field "{field}".',)
            raise

        return tidy_html(html)


async def render_template(
    templates: pathlib.Path, names: list[str], ctx: TemplateContext
) -> str:
    """
    Render the `name`d template from the `templates` directory.

    This is just a convenience wrapper around creating a `TemplateRenderer` and calling
    it's `render` method. For better caching and render performance we should migrate
    all calling code to maintain a single long running `TemplateRenderer` instance.
    """
    return await TemplateRenderer(templates).render(names, ctx)


@jinja2.pass_context
async def _render_filter(ctx: jinja2.runtime.Context, value: Any) -> str:
    """
    Implements a filter than pass HTML through the Jinja renderer.

    This is used so we can put Jinja markup in markdown source pages and have it
    rendered correctly in the output page.
    """
    if not value:
        return value

    if not isinstance(value, str):
        value = str(value)

    try:
        template = ctx.eval_ctx.environment.from_string(value)
        return await template.render_async(**ctx.get_all())
    except Exception:
        LOGGER.exception(f"Failed to render template {value=}")
        raise


def tidy_html(content: str) -> str:
    """
    Simple HTML transformations to make output content tidy-er.

    Current transformations performed:
    - Lines with no non-whitespace characters are removed
    - Repeated line breaks are collapsed
    """
    lines = []
    for source_line in content.splitlines():
        line = source_line.rstrip()
        if line:
            lines.append(line)
    return "\n".join(lines)
