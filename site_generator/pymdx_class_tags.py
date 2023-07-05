from collections.abc import Callable
from xml.etree import ElementTree

import markdown
from markdown import treeprocessors


def _set_class_attribute(element: ElementTree.Element) -> None:
    if element.tag != "div":
        element.set("class", f"content--{element.tag}")


class _ClassTagsProcessor(treeprocessors.Treeprocessor):
    def __init__(
        self, md: markdown.Markdown, cb: Callable[[ElementTree.Element], None]
    ) -> None:
        super().__init__(md)
        self.md: markdown.Markdown = md
        self._cb = cb

    def run(self, root: ElementTree.Element) -> None:
        for element in root.iter():
            self._cb(element)


class ClassTags(markdown.Extension):
    """
    Set the CSS `class` attribute on each element of the generated ElementTree.

    Provide the `callback` kwarg to customise the value of the `class` attribute. By
    default, all non-div tags have their `class` attributes set to
    `f"content--{element.tag}"`.
    """

    config = {"callback": [_set_class_attribute]}  # noqa: RUF012

    def extendMarkdown(self, md: markdown.Markdown) -> None:  # noqa: N802, D102
        md.treeprocessors.register(
            _ClassTagsProcessor(md, self.config["callback"][0]), "class-tags", 0
        )
