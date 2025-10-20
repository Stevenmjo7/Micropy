"""MQTT protocol integration using umqtt.simple."""

try:
    from umqtt.simple import MQTTClient  # type: ignore
except ImportError:  # pragma: no cover - allows linting in CPython
    MQTTClient = object

import ubinascii

from modules.utils.metrics import measure


class MQTTProtocol:
    """Thin wrapper over umqtt.simple to expose telemetry-aware publishing."""

    def __init__(self, config, logger=None):
        """Initialise the MQTT protocol helper.

        Args:
            config: Dictionary with client configuration.
            logger: Optional logger implementation.
        """
        if MQTTClient is object:
            raise RuntimeError("umqtt.simple is required on MicroPython")
        self._cfg = config or {}
        self._logger = logger
        client_id = self._cfg.get("client_id") or self._generate_client_id()
        host = self._cfg.get("host")
        port = self._cfg.get("port", 1883)
        user = self._cfg.get("username")
        password = self._cfg.get("password")
        keepalive = self._cfg.get("keepalive", 60)
        self._topic = self._cfg.get("topic", "telemetry")
        self._client = MQTTClient(client_id, host, port=port, user=user, password=password, keepalive=keepalive)
        if self._logger:
            self._logger.info("MQTT client initialised for %s:%s topic %s", host, port, self._topic)
        self._connect()

    def _generate_client_id(self):
        """Generate a random client id suitable for MQTT."""
        if hasattr(ubinascii, "random"):
            raw = ubinascii.random(6)
        else:  # pragma: no cover - fallback for CPython type checking
            raw = b"pico01"
        return ubinascii.hexlify(raw).decode()

    def _connect(self):
        """Connect the MQTT client to the broker."""
        if self._logger:
            self._logger.info("Connecting to MQTT broker...")
        self._client.connect()
        if self._logger:
            self._logger.info("MQTT connected")

    @measure
    def publish(self, topic, payload):
        """Publish a JSON payload to the configured topic."""
        topic = topic or self._topic
        self._client.publish(topic, payload)
        return {
            "topic": topic,
            "bytes": len(payload),
        }

    def close(self):
        """Disconnect the client if supported."""
        try:
            self._client.disconnect()
        except Exception:  # pragma: no cover - best effort on devices
            pass


__all__ = ["MQTTProtocol"]
