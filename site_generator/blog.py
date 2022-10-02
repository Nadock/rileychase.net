import pathlib

import bs4

from site_generator import config, logging, markdown

LOGGER = logging.getLogger()


async def find_blog_posts(cfg: config.SiteGeneratorConfig, path: pathlib.Path) -> list:
    """
    Generate and return all the additional info the `"blog_index"` page type requires.

    The `path` should be the path to the `"blog_index"` markdown page.
    """
    search_dir = path.parent

    posts = []
    async for post in markdown.find_markdown(search_dir):
        if post == path:
            continue

        # Read post contents & frontmatter
        content, fm = await markdown.load_markdown(cfg, post)
        if not fm.date:
            raise ValueError("Cannot render blog post without a date")

        # Generate a preview of the post
        content = await markdown.render(content)
        first_p = bs4.BeautifulSoup(content, features="html.parser").find("p")
        preview = (
            first_p.get_text()
            if first_p
            else "This page has no paragraphs, please add some content!"
        )

        posts.append(
            {
                "path": f"/{fm.get_output_path().relative_to(cfg.output)}",
                "preview": preview,
                **fm.get_props(),
            }
        )

    # Sort post by their date
    posts.sort(key=lambda p: p["date"])
    return posts
