import sys

from weaving import cli, errors, log

try:
    cli.app.meta()

except KeyboardInterrupt:
    pass

except errors.WeavingError as ex:
    log.logger().error(ex)
    sys.exit(1)

except Exception:
    log.logger().exception("Unhandled error occurred")
    sys.exit(1)
