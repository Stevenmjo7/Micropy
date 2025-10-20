"""Main controller orchestrating sensors and telemetry publishing."""

try:
    import network  # type: ignore
except ImportError:  # pragma: no cover - allows running type-checkers
    network = None

import utime
import ujson
import gc

from core.logger import Logger
from modules.sensors.dht_sensor import DHTSensor
from modules.protocols.mqtt_client import MQTTProtocol
from modules.protocols.http_client import HTTPProtocol
from modules.utils.metrics import enrich


class Controller:
    """High-level orchestrator for the IoT framework."""

    def __init__(self, config):
        """Create the controller using the given configuration dictionary."""
        self.config = config or {}
        self.logger = Logger(self.config.get("device", {}).get("name", "iot"))
        self.interval_ms = self.config.get("interval_ms", 5000)
        self._sensors = []
        self._mqtt = None
        self._http = None
        self._setup_wifi()
        self._init_sensors()
        self._init_protocols()

    def _setup_wifi(self):
        """Initialise Wi-Fi connectivity using the supplied configuration."""
        wifi_cfg = self.config.get("device", {}).get("wifi", {})
        if not wifi_cfg:
            self.logger.warn("No Wi-Fi configuration provided; skipping connection")
            return
        if network is None:
            raise RuntimeError("network module not available. This must run on MicroPython.")
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if not wlan.isconnected():
            self.logger.info("Connecting to Wi-Fi SSID %s", wifi_cfg.get("ssid"))
            wlan.connect(wifi_cfg.get("ssid"), wifi_cfg.get("password"))
            retries = 0
            while not wlan.isconnected() and retries < 50:
                utime.sleep_ms(200)
                retries += 1
        if wlan.isconnected():
            self.logger.info("Wi-Fi connected: %s", wlan.ifconfig())
        else:
            raise RuntimeError("Failed to connect to Wi-Fi")

    def _init_sensors(self):
        """Instantiate sensor modules based on configuration."""
        sensors_cfg = self.config.get("sensors", [])
        for sensor_cfg in sensors_cfg:
            s_type = (sensor_cfg.get("type") or "").lower()
            if s_type == "dht":
                sensor = DHTSensor(
                    name=sensor_cfg.get("name", "dht"),
                    pin=sensor_cfg.get("pin", 15),
                    model=sensor_cfg.get("model", "DHT22"),
                    logger=self.logger,
                )
                self._sensors.append(sensor)
            else:
                self.logger.warn("Unsupported sensor type: %s", s_type)
        if not self._sensors:
            self.logger.warn("No sensors configured")

    def _init_protocols(self):
        """Initialise protocol handlers for MQTT and HTTP."""
        proto_cfg = self.config.get("protocols", {})
        mqtt_cfg = proto_cfg.get("mqtt", {})
        if mqtt_cfg.get("enabled"):
            try:
                self._mqtt = MQTTProtocol(mqtt_cfg, logger=self.logger)
            except Exception as exc:
                self.logger.error("Failed to initialise MQTT: %s", exc)
        http_cfg = proto_cfg.get("http", {})
        if http_cfg.get("enabled"):
            try:
                self._http = HTTPProtocol(http_cfg, logger=self.logger)
            except Exception as exc:
                self.logger.error("Failed to initialise HTTP: %s", exc)

    def _send_to_protocols(self, payload_str):
        """Send the payload to all enabled protocols, collecting metrics."""
        transport_metrics = {}
        if self._mqtt:
            try:
                result, metrics = self._mqtt.publish(None, payload_str)
                transport_metrics["mqtt"] = {
                    "metrics": metrics,
                    "result": result,
                }
            except Exception as exc:
                self.logger.error("MQTT publish failed: %s", exc)
        if self._http:
            try:
                result, metrics = self._http.post(payload_str)
                transport_metrics["http"] = {
                    "metrics": metrics,
                    "result": result,
                }
            except Exception as exc:
                self.logger.error("HTTP post failed: %s", exc)
        return transport_metrics

    def run(self):
        """Start the main control loop."""
        self.logger.info("Starting controller loop with interval %sms", self.interval_ms)
        while True:
            loop_start = utime.ticks_ms()
            transport_logs = []
            for sensor in self._sensors:
                try:
                    data, metrics = sensor.read()
                    payload = enrich(data, metrics, "sensor", sensor.name)
                    payload_str = ujson.dumps(payload)
                    self.logger.debug("Sensor payload: %s", payload_str)
                    proto_metrics = self._send_to_protocols(payload_str)
                    if proto_metrics:
                        transport_logs.append({"sensor": sensor.name, "protocols": proto_metrics})
                except Exception as exc:
                    self.logger.error("Sensor %s read failed: %s", sensor.name, exc)
            loop_duration = utime.ticks_diff(utime.ticks_ms(), loop_start)
            loop_metrics = {
                "latency_ms": loop_duration,
                "mem_delta": 0,
            }
            loop_data = {
                "loop_ms": loop_duration,
                "mem_free": gc.mem_free(),
                "mem_alloc": gc.mem_alloc(),
                "transports": transport_logs,
            }
            loop_payload = enrich(loop_data, loop_metrics, "controller", "main_loop")
            loop_payload_str = ujson.dumps(loop_payload)
            self.logger.debug("Loop metrics payload: %s", loop_payload_str)
            self._send_to_protocols(loop_payload_str)
            utime.sleep_ms(self.interval_ms)


__all__ = ["Controller"]
