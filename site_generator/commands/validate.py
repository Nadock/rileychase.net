import sys

from site_generator import config, logging, markdown

LOGGER = logging.getLogger()


def validate(cfg: config.SiteGeneratorConfig):
    """Validate CLI command handler; check files for semantic validation issues."""

    async def _validate():
        _errors = []
        async for page in markdown.find_markdown(cfg.pages):
            content, fm = await markdown.load_markdown(page)
            fm.config = cfg

            if not content:
                _errors.append(
                    f"{cfg.format_relative_path(page)}: content: page is empty"
                )

            for fm_err in fm.validate_frontmatter():
                _errors.append(
                    f"{cfg.format_relative_path(page)}: frontmatter: {fm_err}"
                )

        if not _errors:
            return

        for err in _errors:
            LOGGER.error(err)
        sys.exit(1)

    return _validate
