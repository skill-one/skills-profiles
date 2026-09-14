"""Logging configuration."""

import logging
import sys


def setup_logging(debug: bool = False) -> None:
    """Configure logging: INFO by default, DEBUG with --debug."""
    level = logging.DEBUG if debug else logging.INFO
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logging.basicConfig(level=level, handlers=[handler], force=True)
    logging.getLogger("httpx").setLevel(logging.WARNING)
