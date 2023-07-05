import datetime
import pathlib
from typing import Any, Literal
from urllib import parse

import pydantic

from site_generator import config as _config
from site_generator import emoji


class PageFrontmatter(pydantic.BaseModel):
    """
    Frontmatter values extracted from markdown page frontmatter content.

    `template` is the name of the template to use when rendering this file

    `path` the path under which the page served in the output. If this path does not
    end in `.html` it will have `index.html` appended so the path works as expected
    in browsers.

    `title`, `subtitle`, `description`, `date`, and `tags` can each be used to describe
    the page and it's content. It depends on the template how these are used, for
    example you can use the `title` to set the `.head.title` DOM field's text.

    `image` is a URL or path to an image to use in the Open Graph preview.

    `type` is a special keyword that enable bespoke page handling. You normally do not
    need to specify this value, the default has no special meaning. However, you can
    set the page `type` to one of the following values to enable specific
    functionality.
      - `"default"` is the default value and has no special meaning.
      - `"blog_index"` marks this page as the root page for a blog. When being
        processed, this file will use the `blog_index` pipeline instead of the default
        `markdown` pipeline. The file must be named `index.md`.

    `meta` is a dict of arbitrary values that can be set on a per-page basis with no
    further validation or prescribed semantic meaning. It depends on the template
    how these values are used.
    """

    template: str | None = None
    path: str | None = None
    title: str | None = None
    subtitle: str | None = None
    image: str | None = None
    description: str | None = None
    tags: list[str] = pydantic.Field(default_factory=list)
    date: datetime.date | None = None
    type: Literal["default"] | Literal["blog_index"] = "default"  # noqa: A003

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

    def get_page_url(self) -> str:
        """
        Determine the URL to this page in the rendered site based on it's output path
        and the base URL.
        """
        if not self.config:
            raise ValueError(f"{self.__class__.__name__}.config must be set")

        path = "/" + str(self.get_output_path().relative_to(self.config.output))
        path = path.removesuffix("index.html")

        return self.config.base_url() + path

    def get_image_url(self) -> str | None:
        """Returns the `PageFrontmatter.image` value as a fully qualified URL."""
        if not self.config:
            raise ValueError(f"{self.__class__.__name__}.config must be set")

        if not self.image:
            return None
        if parse.urlparse(self.image).hostname:
            return self.image

        image = self.image if self.image.startswith("/") else "/" + self.image
        return self.config.base_url() + image

    def get_props(self) -> dict[str, Any]:
        """
        Return the frontmatter properties as a `dict` of values.

        Frontmatter "properties" are any frontmatter values that might be included in
        the rendered output, like the `title`.
        """
        props = {
            **self.model_dump(exclude={"meta", "config", "file"}),
            "title": emoji.replace_emoji(self.title),
            "subtitle": emoji.replace_emoji(self.subtitle),
            "description": emoji.replace_emoji(self.description),
            "image": self.get_image_url(),
            "url": self.get_page_url(),
        }
        return {k: v for k, v in props.items() if v is not None}

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

        if not self.image and validation.get("image", True):
            errors.append("no image set")

        if not self.description and validation.get("description", True):
            errors.append("no description set")

        if self.type == "blog_index" and self.file.name != "index.md":
            errors.append("type set to 'blog_index' but file not named `index.md`")

        return errors
