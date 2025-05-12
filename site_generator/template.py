import pathlib
import re
from typing import Any

import jinja2

from site_generator import logging

LOGGER = logging.getLogger()


class TemplateRenderer:
    """Render templates in a persistent Jinja environment."""

    def __init__(self, templates: pathlib.Path) -> None:
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(templates),
            autoescape=True,
            enable_async=True,
        )
        self.env.filters["render"] = _render_filter

    async def render(self, names: list[str], **ctx: dict) -> str:
        """Render the named template with the provided render context."""
        template = self.env.get_or_select_template([n for n in names if n])

        try:
            html = await template.render_async(**ctx)
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
    templates: pathlib.Path, names: list[str], **render_kwargs: dict[str, Any]
) -> str:
    """
    Render the `name`d template from the `templates` directory.

    This is just a convenience wrapper around creating a `TemplateRenderer` and calling
    it's `render` method. For better caching and render performance we should migrate
    all calling code to maintain a single long running `TemplateRenderer` instance.
    """
    return await TemplateRenderer(templates).render(names, **render_kwargs)


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
