import datetime
import math
import pathlib

import bs4

from weaving import config, frontmatter, logging, markdown, template

LOGGER = logging.getLogger()


async def find_blog_posts(
    cfg: config.SiteGeneratorConfig, path: pathlib.Path
) -> list[template.BlogIndexPostContext]:
    """
    Generate and return all the additional info the `"blog_index"` page type requires.

    The `path` should be the path to the `"blog_index"` markdown page.
    """
    search_dir = path.parent

    posts: list[template.BlogIndexPostContext] = []
    async for post in markdown.find_markdown(search_dir):
        if post == path:
            continue

        # Read post contents & frontmatter
        content, fm = await markdown.load_markdown(cfg, post)
        if not fm.date:
            raise ValueError("Cannot render blog post without a date")
        if fm.debug and not cfg.debug_pages:
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

        posts.append(template.BlogIndexPostContext(frontmatter=fm, preview=preview))

    # Sort post by their date
    def sort_frontmatter(t: template.BlogIndexPostContext) -> datetime.date:
        if not t.frontmatter.date:
            raise ValueError("Cannot render blog post without a date")
        return t.frontmatter.date

    posts.sort(key=sort_frontmatter, reverse=True)
    return posts


async def blog_index_pipeline(
    cfg: config.SiteGeneratorConfig,
    path: pathlib.Path,
    fm: frontmatter.PageFrontmatter,
    ctx: template.TemplateContext,
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
    max_pages = math.ceil(len(posts) / page_size)

    for page_idx in range(0, len(posts), page_size):
        current_page = (page_idx // page_size) + 1

        ctx = template.BlogIndexTemplateContext(
            **ctx.model_dump(),
            posts=posts[page_idx : page_idx + page_size],
            current_page=current_page,
            max_pages=max_pages,
        )
        html = await template.jinja(cfg.templates).render(ctx)

        if page_idx == 0:
            root_output.parent.mkdir(parents=True, exist_ok=True)
            root_output.write_text(html)

            output = root_output.parent / "_" / "1" / "index.html"
            output.parent.mkdir(parents=True, exist_ok=True)

            output.write_text(
                "<html>"
                "<head>"
                '<meta http-equiv="refresh" content="0; '
                f'url=/{root_output.parent.relative_to(cfg.output)!s}"/>'
                "</head>"
                "</html>"
            )
        else:
            output = root_output.parent / "_" / str(current_page) / "index.html"
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(html)

        LOGGER.debug(
            f"wrote blog posts {page_idx} to {page_idx + page_size} to {output}"
        )

    return root_output
