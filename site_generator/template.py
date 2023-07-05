import pathlib
from typing import Any

import jinja2

from site_generator import logging

LOGGER = logging.getLogger()


async def render_template(
    templates: pathlib.Path, name: str, **render_kwargs: dict[str, Any]
) -> str:
    """Render the `name`d template from the `templates` directory."""
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates), autoescape=True)
    env.filters["render"] = _render_filter

    template = env.get_or_select_template(name)
    return template.render(**render_kwargs)


@jinja2.pass_context
def _render_filter(ctx: jinja2.runtime.Context, value: str) -> str:
    if not value:
        return value

    if not isinstance(value, str):
        value = str(value)

    try:
        template = ctx.eval_ctx.environment.from_string(value)
        return template.render(**ctx.get_all())
    except Exception as ex:
        LOGGER.error(f"Failed to render template {value=}: {ex}")
        raise
