import math
import pathlib

import bs4

from site_generator import config, frontmatter, logging, markdown, template

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
        if fm.type == "debug" and not cfg.debug_pages:
            LOGGER.debug(f"Skipping debug blog page: {path}")
            continue

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
                "path": fm.get_page_url(),
                "preview": preview,
                **fm.get_props(),
            }
        )

    # Sort post by their date
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


async def blog_index_pipeline(
    cfg: config.SiteGeneratorConfig,
    path: pathlib.Path,
    fm: frontmatter.PageFrontmatter,
    render_kwargs: dict,
) -> pathlib.Path:
    """
    Render pipeline for a `blog_index` page, returning the path to the first rendered
    output page.

    To avoid having one massive index page, the a blog index is paginated into `N`
    pages. The paginated pages are written out to the sub path
    `/_/${page_num}/index.html` relative to the first index page. The number `1`
    page is also written out as a redirect to the first index page for convenience.
    """
    posts = await find_blog_posts(cfg, path)
    root_output = fm.get_output_path()

    page_size = cfg.blog_posts_per_page
    page_count = math.ceil(len(posts) / page_size)

    for page in range(0, len(posts), page_size):
        render_kwargs["blog"] = {
            "posts": posts[page : page + page_size],
            "page_count": page_count,
            "current_page": page + 1,
        }

        html = await template.render_template(
            templates=cfg.templates,
            name=fm.get_template_name(),
            **render_kwargs,
        )

        if page == 0:
            root_output.parent.mkdir(parents=True, exist_ok=True)
            root_output.write_text(html)

            output = root_output.parent / "_" / str(page + 1) / "index.html"
            output.parent.mkdir(parents=True, exist_ok=True)

            output.write_text(
                "<html>"
                "<head>"
                '<meta http-equiv="refresh" content="0; '
                f'url=/{root_output.parent.relative_to(cfg.output)!s}"/>'
                "</head>"
                "</html>"
            )

            LOGGER.debug(
                f"wrote blog posts {page} to {page + page_size} to {root_output}"
            )
        else:
            output = root_output.parent / "_" / str(page + 1) / "index.html"
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(html)

            LOGGER.debug(f"wrote blog posts {page} to {page + page_size} to {output}")

    return root_output
