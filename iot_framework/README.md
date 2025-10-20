# Pico W IoT Modular Framework (MicroPython)

Este proyecto implementa un framework IoT modular para la Raspberry Pi Pico W, inspirado en una arquitectura tipo plugin. El objetivo es facilitar la lectura de sensores, la publicación de telemetría y la recolección de métricas de rendimiento en tiempo real.

## ⚙️ Características principales

- Configuración declarativa mediante `config.json`.
- Arquitectura modular con sensores y protocolos desacoplados.
- Decorador `@measure` para calcular latencia y consumo de memoria en cada operación.
- Publicación de telemetría enriquecida con métricas del dispositivo y del ciclo principal.
- Soporte para MQTT (usando `umqtt.simple`) y HTTP (`urequests`).

## 📁 Estructura del proyecto

```
/iot_framework/
├── main.py
├── config.json
├── core/
│   ├── controller.py
│   └── logger.py
├── modules/
│   ├── sensors/
│   │   └── dht_sensor.py
│   ├── protocols/
│   │   ├── mqtt_client.py
│   │   └── http_client.py
│   └── utils/
│       └── metrics.py
└── README.md
```

## 🔌 Conexión de hardware

1. Conecta el sensor DHT11/DHT22 al pin GPIO configurado en `config.json` (por defecto GPIO 15).
2. Alimenta el sensor con 3V3 y GND de la Pico W.
3. Asegúrate de usar resistencias pull-up según las recomendaciones del fabricante del sensor DHT.

## 📶 Configuración Wi-Fi

Edita `config.json` y establece las credenciales de tu red:

```json
"wifi": {
  "ssid": "TU_RED_WIFI",
  "password": "TU_PASSWORD"
}
```

## 🚀 Puesta en marcha

1. **Instala MicroPython 1.22+** en la Pico W desde [la guía oficial](https://docs.micropython.org/en/latest/rp2/tutorial/intro.html).
2. Copia la carpeta `iot_framework/` completa al sistema de archivos de la Pico W (por ejemplo con `mpremote cp -r`).
3. Ajusta los parámetros de `config.json` (intervalos, topics MQTT, endpoint HTTP, etc.).
4. Reinicia la Pico W o ejecuta `main.py` manualmente:

   ```bash
   mpremote run iot_framework/main.py
   ```

## 📡 Dependencias en el dispositivo

- `umqtt.simple` (incluido en MicroPython).
- `urequests` (instalar con `mpremote mip install urequests` si deseas usar HTTP).
- Módulos estándar de MicroPython: `network`, `gc`, `utime`, `ujson`.

## 🧪 Ejemplo de salida en consola

```
[12345] INFO pico-iot: Wi-Fi connected: ('192.168.1.50', '255.255.255.0', '192.168.1.1', '8.8.8.8')
[12500] INFO pico-iot: Starting controller loop with interval 5000ms
[17510] DEBUG pico-iot: Sensor payload: {"component": "sensor", "name": "ambient_dht", "ts_ms": 17510, "metrics": {"latency_ms": 35, "mem_delta": -96}, "data": {"temperature_c": 25.4, "humidity_pct": 56.2}, "sys_mem": {"mem_free": 93248, "mem_alloc": 11392}}
[17520] DEBUG pico-iot: Loop metrics payload: {"component": "controller", "name": "main_loop", "ts_ms": 17520, "metrics": {"latency_ms": 20, "mem_delta": 0}, "data": {"loop_ms": 20, "mem_free": 93184, "mem_alloc": 11456, "transports": [{"sensor": "ambient_dht", "protocols": {"mqtt": {"metrics": {"latency_ms": 18, "mem_delta": -64}, "result": {"topic": "devices/pico-iot/telemetry", "bytes": 198}}}}]}, "sys_mem": {"mem_free": 93152, "mem_alloc": 11488}}
```

Esta salida ilustra cómo cada lectura y ciclo incluyen métricas de latencia, consumo de memoria y publicación.

## 🛠 Personalización

- Agrega nuevos sensores creando módulos bajo `modules/sensors/` y utilizando el decorador `@measure`.
- Implementa protocolos adicionales en `modules/protocols/` que expongan métodos medidos para publicar datos.
- Ajusta `interval_ms` en `config.json` para controlar la frecuencia del ciclo principal.

## 🧾 Licencia

Libre uso para proyectos personales y educativos. Ajusta según tus necesidades.
