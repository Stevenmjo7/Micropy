"""DHT temperature/humidity sensor module."""

try:
    import dht  # type: ignore
    from machine import Pin  # type: ignore
except ImportError:  # pragma: no cover - allows linting in CPython
    dht = None
    Pin = object

from modules.utils.metrics import measure


class DHTSensor:
    """Wrapper around the DHT11/DHT22 sensor with telemetry integration."""

    def __init__(self, name, pin, model="DHT22", logger=None):
        """Create a new DHT sensor instance.

        Args:
            name: Logical name for the sensor.
            pin: GPIO number where the sensor data pin is connected.
            model: Either "DHT11" or "DHT22" (default).
            logger: Optional logger for debug output.
        """
        self.name = name
        self._pin = pin
        self._model = (model or "DHT22").upper()
        self._logger = logger
        self._sensor = None
        self._setup()

    def _setup(self):
        """Initialise the underlying DHT object."""
        if dht is None:
            raise RuntimeError("DHT module not available. This code must run on MicroPython.")
        pin = Pin(self._pin)
        if self._model == "DHT11":
            self._sensor = dht.DHT11(pin)
        else:
            self._sensor = dht.DHT22(pin)
        if self._logger:
            self._logger.info("DHT sensor '%s' initialised on pin %s (%s)", self.name, self._pin, self._model)

    @measure
    def read(self):
        """Read the sensor values and return a dictionary."""
        if self._sensor is None:
            raise RuntimeError("Sensor not initialised")
        self._sensor.measure()
        temperature = self._sensor.temperature()
        humidity = self._sensor.humidity()
        return {
            "temperature_c": temperature,
            "humidity_pct": humidity,
        }


__all__ = ["DHTSensor"]
