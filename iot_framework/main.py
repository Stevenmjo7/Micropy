"""Entry point for the Pico W IoT framework."""

import ujson

from core.controller import Controller
from core.logger import Logger


def load_config(path="config.json"):
    """Load configuration from JSON file."""
    with open(path, "r") as handle:
        return ujson.loads(handle.read())


def main():
    """Initialise and start the IoT controller."""
    logger = Logger("main")
    try:
        config = load_config()
    except OSError as exc:
        logger.error("Configuration file missing: %s", exc)
        raise
    controller = Controller(config)
    try:
        controller.run()
    except KeyboardInterrupt:
        logger.warn("Execution interrupted by user")
    except Exception as exc:
        logger.error("Controller failure: %s", exc)
        raise


if __name__ == "__main__":
    main()
