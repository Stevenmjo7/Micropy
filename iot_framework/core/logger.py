"""Lightweight logger compatible with MicroPython."""

import utime


class Logger:
    """A minimal logger that writes formatted messages to stdout."""

    def __init__(self, name="iot", level="INFO"):
        self.name = name
        self.level = level
        self._levels = {"DEBUG": 10, "INFO": 20, "WARN": 30, "ERROR": 40}

    def _should_log(self, level):
        return self._levels.get(level, 20) >= self._levels.get(self.level, 20)

    def _log(self, level, message, *args):
        if not self._should_log(level):
            return
        timestamp = utime.ticks_ms()
        if args:
            message = message % args
        print("[%s] %s %s: %s" % (timestamp, level, self.name, message))

    def debug(self, message, *args):
        """Log a debug message."""
        self._log("DEBUG", message, *args)

    def info(self, message, *args):
        """Log an info message."""
        self._log("INFO", message, *args)

    def warn(self, message, *args):
        """Log a warning message."""
        self._log("WARN", message, *args)

    def error(self, message, *args):
        """Log an error message."""
        self._log("ERROR", message, *args)


__all__ = ["Logger"]
