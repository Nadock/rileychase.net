import pathlib

import aiofile
import yaml

from weaving import errors, models


async def new_markdown(path: pathlib.Path, fm: models.PageFrontmatter) -> pathlib.Path:
    """Create a new markdown file with the provided frontmatter."""
    fm_data = fm.model_dump(
        exclude_none=True,
        include={
            "type",
            "debug",
            "template",
            "title",
            "subtitle",
            "description",
        },
    )
    if fm_data.get("debug") is False:
        del fm_data["debug"]

    content = yaml.safe_dump(
        fm_data,
        indent=2,
        explicit_start=True,
        explicit_end=False,
        sort_keys=False,
        allow_unicode=True,
    )
    content += "---"

    return await _write_new_file(path, content)


async def new_html(path: pathlib.Path) -> pathlib.Path:
    """Create a new HTML template file."""
    content = "{# https://jinja.palletsprojects.com/en/stable/templates/ #}\n"
    return await _write_new_file(path, content)


async def _write_new_file(path: pathlib.Path, content: str) -> pathlib.Path:
    if path.exists():
        raise errors.WeavingError(f"File already exists: {path}")

    path.parent.mkdir(exist_ok=True, parents=True)
    async with aiofile.async_open(path, "w") as f:
        await f.write(content)

    return path
