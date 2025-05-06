import pathlib
import re

import jinja2

from weaving import models


class TemplateRenderer:
    """Render templates in a persistent Jinja environment."""

    def __init__(self, templates: pathlib.Path) -> None:
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(templates),
            autoescape=True,
            auto_reload=False,
            enable_async=True,
        )
        # self.env.filters["render"] = _render_filter

    async def render(self, ctx: models.TemplateContext) -> str:
        """Render the named template with the provided render context."""
        template = self.env.get_or_select_template(ctx.frontmatter.get_template())

        try:
            html = await template.render_async(context=ctx)
        except jinja2.TemplateError as ex:
            if (
                ex.message
                and (match := re.match(r"'(?P<field>.+)' is undefined", ex.message))
                and (field := match.group("field"))
            ):
                ex.args = (f'Unknown template context field "{field}".',)

            raise

        return tidy_html(html)


@jinja2.pass_context
def _render_filter(ctx: jinja2.runtime.Context, value: str) -> str:
    # TODO(Nadock): It's possible we don't need this filter function. Consider removing,
    #               or at least properly documenting.
    if not value:
        return value

    if not isinstance(value, str):
        value = str(value)

    template = ctx.eval_ctx.environment.from_string(value)
    return template.render(**ctx.get_all())


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
