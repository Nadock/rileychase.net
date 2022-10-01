import pathlib

from site_generator import config, logging, markdown

LOGGER = logging.getLogger()


async def blog_index_render_info(
    cfg: config.SiteGeneratorConfig, path: pathlib.Path
) -> dict:
    """
    Generate and return all the additional info the `"blog_index"` page type requires.

    The `path` should be the path to the `"blog_index"` markdown page.
    """
    posts = []
    async for post in markdown.find_markdown(path.parent):
        _, fm = await markdown.load_markdown(post)
        fm.config = cfg
        post_path = post.relative_to(path.parent)
        if post_path == pathlib.Path("index.md"):
            continue
        if not fm.date:
            raise ValueError(f"Cannot render blog post without a date: {post_path}")

        posts.append(
            {
                "path": f"/{fm.get_output_path().relative_to(cfg.output)}",
                "fm": fm,
            }
        )

    posts.sort(key=lambda p: p["fm"].date)
    return {
        "posts": posts,
    }
