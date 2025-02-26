from __future__ import annotations

# Must not be in a type checking block for Pydantic
import datetime  # noqa: TC003
import pathlib
from typing import Any, Literal
from urllib import parse

import pydantic

from site_generator import config as _config
from site_generator import emoji

PageType = Literal["default", "blog_index", "debug"]


class OpenGraphFrontmatter(pydantic.BaseModel):
    """Page Open Graph details extracted from markdown frontmatter content."""

    title: str | None = None
    """The og:title for this page, defaults to the page title if not set."""

    image: str | None = None
    """The og:image for this page."""

    description: str | None = None
    """The og:description for this page, defaults to the page subtitle if not set."""

    url: str | None = None
    """The og:url for this page, defaults to the computed page URL if not set."""

    type: str = "website"
    """The og:type for this page, defaults to `"website"` if not set."""

    locale: str | None = None
    """The og:locale for this page, defaults to the locale in config if not set.."""

    site_name: str | None = None
    """
    The og:site_name for this page, defaults to the site name in config if not set.
    """


class PageFrontmatter(pydantic.BaseModel):
    """Page details extracted from markdown frontmatter content."""

    template: str | None = None
    """The name of the template to use when rendering this file."""

    path: str | None = None
    """
    The path under which the page served in the output. If this path does not end in
    `.html` it will have `index.html` appended so it works as expected in browsers.
    """

    title: str | None = None
    """The title for this page."""

    subtitle: str | None = None
    """The subtitle for this page."""

    description: str | None = None
    """The meta description for this page."""

    tags: list[str] = pydantic.Field(default_factory=list)
    """Classification tags for this page's content."""

    date: datetime.date | None = None
    """The original publication date for this page."""

    og: OpenGraphFrontmatter | None = None
    """
    Open Graph details. Some values are auto populated from `title`, `subtitle`, `date`,
    and other sources.
    """

    meta: dict | None = None
    """
    Arbitrary values that can be set on a per-page basis with no further validation or
    prescribed semantic meaning. It depends on the template how these values are used.
    """

    type: PageType = "default"
    """
    `type` is a special keyword that enable bespoke page handling. You normally do not
    need to specify this value, the default has no special meaning. However, you can
    set the page `type` to one of the following values to enable specific
    functionality.

    - `default` is the default value and has no special meaning.
    - `blog_index` marks this page as the root page for a blog. When being processed,
       this file will use the `blog_index` pipeline instead of the default `markdown`
       pipeline. The file must be named `index.md`.
    - `debug` marks this page for local preview only, not to be included in the full
       site build.
    """

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

    def get_open_graph(self) -> OpenGraphFrontmatter:
        """
        Returns the Open Graph frontmatter for this page with default values applied.

        The values actually provided via frontmatter from the source file remain
        unmodified in `self.og`.
        """
        if not self.config:
            raise ValueError(f"{self.__class__.__name__}.config must be set")

        og = self.og or OpenGraphFrontmatter()

        # Make OG image URL fully qualified if it isn't already
        if og.image and not parse.urlparse(og.image).hostname:
            image = og.image if og.image.startswith("/") else "/" + og.image
            og.image = self.config.base_url() + "/" + image

        # Set default values for OG properties
        og.title = og.title or self.title
        og.description = og.description or self.subtitle
        og.url = og.url or self.get_page_url()
        og.locale = og.locale or self.config.locale
        og.site_name = og.site_name or self.config.site_name

        return og

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
            "og": self.get_open_graph(),
        }
        return {k: v for k, v in props.items() if v is not None}

    def get_meta(self) -> dict[str, Any]:
        """
        Return the frontmatter meta content as a `dict` of values.

        Frontmatter "meta" values are the frontmatter values that aren't used directly
        in the page render but are used in other parts of the process, such as the
        `path` meta property.
        """
        meta = self.model_dump(include={"meta"}).get("meta", {})
        return meta if isinstance(meta, dict) else {}

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

        if self.type == "blog_index" and self.file.name != "index.md":
            errors.append("type set to 'blog_index' but file not named `index.md`")

        return errors
