import pathlib

import jinja2

from site_generator import logging

LOGGER = logging.getLogger()


async def render_template(templates: pathlib.Path, name: str, **render_kwargs) -> str:
    """Render the `name`d template from the `templates` directory."""
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates))
    template = env.get_or_select_template(name)
    return template.render(**render_kwargs)
