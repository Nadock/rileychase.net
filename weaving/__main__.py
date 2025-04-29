import sys

from weaving import cli, error, log

try:
    cli.app.meta()

except KeyboardInterrupt:
    pass

except error.WeavingError as ex:
    log.logger().error(ex)
    sys.exit(1)

except Exception:
    log.logger().exception("Unhandled error occurred")
    sys.exit(1)
