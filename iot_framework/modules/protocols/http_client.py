"""HTTP protocol integration for posting telemetry."""

try:
    import urequests  # type: ignore
except ImportError:  # pragma: no cover - allows linting in CPython
    urequests = None

from modules.utils.metrics import measure


class HTTPProtocol:
    """Simple HTTP client to send telemetry to an HTTP endpoint."""

    def __init__(self, config, logger=None):
        """Create the protocol helper."""
        if urequests is None:
            raise RuntimeError("urequests module not available. Install it on the device.")
        self._cfg = config or {}
        self._logger = logger
        self._url = self._cfg.get("url")
        self._headers = self._cfg.get("headers") or {"Content-Type": "application/json"}
        if self._logger:
            self._logger.info("HTTP client initialised for %s", self._url)

    @measure
    def post(self, payload):
        """POST the given payload to the configured endpoint."""
        response = urequests.post(self._url, data=payload, headers=self._headers)
        try:
            status = response.status_code
            text = response.text
        finally:
            response.close()
        return {
            "status": status,
            "response": text,
        }


__all__ = ["HTTPProtocol"]
