import datetime
import pathlib
from typing import Any

import pydantic

from site_generator import config as _config
from site_generator import emoji


class PageFrontmatter(pydantic.BaseModel):  # pylint: disable=no-member
    """
    Frontmatter values extracted from markdown page frontmatter content.

    `template` is the name of the template to use when rendering this file

    `path` the path under which the page served in the output. If this path does not
    end in `.html` it will have `index.html` appended so the path works as expected
    in browsers.

    `title`, `subtitle`, `description`, and `tags` can each be used to describe the
    page and it's content. It depends on the template how these are used, for example
    you can use the `title` to set the `.head.title` DOM field's text.

    `meta` is a dict of arbitrary values that can be set on a per-page basis with no
    further validation or prescribed semantic meaning. It depends on the template
    how these values are used.
    """

    template: str | None = None
    path: str | None = None
    title: str | None = None
    subtitle: str | None = None
    description: str | None = None
    tags: list[str] = pydantic.Field(default_factory=list)
    date: datetime.date | None = None

    meta: dict | None = None

    # The following fields are populated automatically, don't need to be in the
    # template frontmatter, and aren't included in template rendering.
    file: pathlib.Path
    config: _config.SiteGeneratorConfig | None = None

    def get_template_name(self) -> str:
        """Determine the template name to use in rendering the associated page."""
        if not self.config:
            raise ValueError(f"{self.__class__.__name__}.config must be set")

        if self.template:
            return self.template
        if self.config.default_template:
            return self.config.default_template
        return "default.html"

    def get_output_path(self) -> pathlib.Path:
        """Determine the output path to write rendered page content into."""
        if not self.config:
            raise ValueError(f"{self.__class__.__name__}.config must be set")

        if self.path and self.path.startswith("/"):
            self.path = self.path[1:]

        if not self.path:
            base = self.file.parent.relative_to(self.config.pages)
            name = self.file.name.replace(".md", ".html")
            path = base / name
        else:
            path = pathlib.Path(self.path)

        path = (self.config.output / path).resolve()
        if not path.name.endswith(".html"):
            path = path / "index.html"

        return path

    def get_props(self) -> dict[str, Any]:
        """
        Return the frontmatter properties as a `dict` of values.

        Frontmatter "properties" are any frontmatter values that might be included in
        the rendered output, like the `title`.
        """
        return {
            **self.dict(exclude={"meta", "config", "file"}, exclude_none=True),
            **{
                "title": emoji.replace_emoji(self.title),
                "subtitle": emoji.replace_emoji(self.subtitle),
                "description": emoji.replace_emoji(self.description),
            },
        }

    def get_meta(self) -> dict[str, Any]:
        """
        Return the frontmatter meta content as a `dict` of values.

        Frontmatter "meta" values are the frontmatter values that aren't used directly
        in the page render but are used in other parts of the process, such as the
        `path` meta property.
        """
        return self.dict(include={"meta"}).get("meta", {})

    def validate_frontmatter(self) -> list[str]:
        """
        Analyse the configured frontmatter values for sematic correctness.

        The validation is above and beyond the Pydantic validation, and is aimed at
        determining if a page's frontmatter is likely to cause build issues.
        """
        errors = []
        validation = self.meta.get("validation", {}) if self.meta else {}

        if not self.title and validation.get("title", True):
            errors.append("no title set")

        if not self.subtitle and validation.get("subtitle", True):
            errors.append("no subtitle set")

        if not self.description and validation.get("description", True):
            errors.append("no description set")

        return errors
