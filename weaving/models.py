import datetime
from typing import Annotated, Literal

import pydantic

from weaving import emoji

EmojiStr = Annotated[
    str, pydantic.PlainSerializer(lambda s: emoji.replace_emoji(s), return_type=str)
]

PageType = Literal["default", "blog", "blog_index"]


class OpenGraphFrontmatter(pydantic.BaseModel):
    """Page Open Graph details extracted from markdown frontmatter content."""

    title: str | None = None
    """The og:title for the page, defaults to the page title if not set."""

    image: str | None = None
    """The og:image URL for the page."""

    description: str | None = None
    """The og:description for the page, defaults to the page subtitle if not set."""

    url: str | None = None
    """The og:url for the page, defaults to the computed page URL if not set."""

    type: str = "website"
    """The og:type for the page, defaults to `"website"` if not set."""

    locale: str | None = None
    """The og:locale for the page."""

    site_name: str | None = None
    """The og:site_name for this page."""


class PageFrontmatter(pydantic.BaseModel):
    """Page details extracted from markdown frontmatter content."""

    type: PageType = "default"

    debug: bool = False
    """
    Indicates the page is for debug purposes and is not included in site builds by
    default.
    """

    template: str | None = None
    """The name of the template to use when rendering the page."""

    title: EmojiStr = ""
    """The title for the page."""

    subtitle: EmojiStr = ""
    """The subtitle for the page."""

    description: EmojiStr = ""
    """The meta description for this page."""

    og: OpenGraphFrontmatter | None = None
    """
    Open Graph details. Some values are auto populated from `title`, `subtitle`, `date`,
    and other sources.
    """

    meta: dict = pydantic.Field(default_factory=dict)
    """
    Arbitrary values that can be set on a per-page basis with no further validation or
    prescribed semantic meaning. It depends on the template how these values are used.
    """

    def get_template(self) -> str:
        return self.template or f"{self.type}.html"


class TemplateContext(pydantic.BaseModel):
    content: str
    frontmatter: PageFrontmatter
    rendered_at: datetime.datetime
    modified_at: datetime.datetime
    git_ref: str | None
