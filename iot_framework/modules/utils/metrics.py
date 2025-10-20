"""Utility helpers for measuring performance and enriching telemetry payloads."""

import gc
import utime


def mem_snapshot():
    """Return a snapshot of the current memory usage."""
    gc.collect()
    return {
        "mem_free": gc.mem_free(),
        "mem_alloc": gc.mem_alloc(),
    }


def measure(fn):
    """Decorator that measures latency (ms) and memory delta for the wrapped function."""

    def wrapper(*args, **kwargs):
        gc.collect()
        mem_before = gc.mem_free()
        start = utime.ticks_ms()
        result = fn(*args, **kwargs)
        latency = utime.ticks_diff(utime.ticks_ms(), start)
        gc.collect()
        mem_after = gc.mem_free()
        mem_delta = mem_after - mem_before
        metrics = {
            "latency_ms": latency,
            "mem_delta": mem_delta,
        }
        return result, metrics

    return wrapper


def enrich(result, metrics, component, name):
    """Compose a full telemetry payload including metrics and system memory info."""
    payload = {
        "component": component,
        "name": name,
        "ts_ms": utime.ticks_ms(),
        "metrics": metrics,
        "data": result,
        "sys_mem": mem_snapshot(),
    }
    return payload


__all__ = ["mem_snapshot", "measure", "enrich"]
