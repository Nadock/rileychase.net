import sys
from collections.abc import Callable

from site_generator import config, logging, validation

LOGGER = logging.getLogger()


def validate(cfg: config.SiteGeneratorConfig) -> Callable:
    """Validate CLI command handler; check files for semantic validation issues."""

    async def validate() -> None:
        LOGGER.info("Starting site validation")

        count = 0
        async for error in validation.Validator(cfg).validate():
            error_msg = f"[{error.file.relative_to(cfg.base)}] {error.error}"
            if error.line and error.char:
                error_msg += f" on line {error.line}, column {error.char}"
            LOGGER.error(error_msg)
            count += 1

        if count > 0:
            LOGGER.error(f"{count} validation error{'s' if count > 1 else ''} found")
            sys.exit(count)

        LOGGER.info("No validation errors found")

    return validate
