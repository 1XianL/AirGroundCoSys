from __future__ import annotations

from dataclasses import dataclass
import random
from typing import List

import numpy as np

from .config import SimulationConfig


@dataclass(frozen=True)
class SensorReading:
    sensor_id: str
    value: float
    normalized_value: float
    status: str
    unit: str


@dataclass(frozen=True)
class Snapshot:
    readings: List[SensorReading]
    line_history: np.ndarray
    heatmap: np.ndarray
    summary_values: dict[str, float]


class SensorDataSimulator:
    """Generates periodic synthetic industrial monitoring data."""

    UNITS = ("ppm", "kPa", "degC", "%RH", "m3/h")

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self.rng = random.Random(config.seed)
        self.value_min = config.value_range.min
        self.value_max = config.value_range.max
        self.span = self.value_max - self.value_min
        self.current_values = [
            self.rng.uniform(self.value_min + 0.2 * self.span, self.value_max - 0.2 * self.span)
            for _ in range(config.num_sensors)
        ]
        self.history_length = 28
        self.history = np.zeros((config.num_sensors, self.history_length), dtype=np.float32)
        for sensor_index, value in enumerate(self.current_values):
            self.history[sensor_index, :] = value

    def generate_snapshot(self) -> Snapshot:
        updated_values = []
        for sensor_index, previous_value in enumerate(self.current_values):
            base_target = self.value_min + (sensor_index + 1) / (self.config.num_sensors + 1) * self.span
            drift = (base_target - previous_value) * self.config.update_behavior.drift_strength
            noise = self.rng.uniform(-1.0, 1.0) * self.span * self.config.update_behavior.volatility
            next_value = previous_value + drift + noise

            if self.rng.random() < self.config.update_behavior.anomaly_probability:
                spike = self.span * self.config.update_behavior.spike_scale
                next_value += self.rng.choice((-spike, spike))

            next_value = max(self.value_min, min(self.value_max, next_value))
            updated_values.append(next_value)

        self.current_values = updated_values
        self.history = np.roll(self.history, -1, axis=1)
        self.history[:, -1] = np.array(self.current_values, dtype=np.float32)

        readings = []
        for sensor_index, value in enumerate(self.current_values):
            normalized = (value - self.value_min) / self.span if self.span else 0.0
            readings.append(
                SensorReading(
                    sensor_id=f"S-{sensor_index + 1:02d}",
                    value=round(value, 2),
                    normalized_value=normalized,
                    status=self._status_for_value(normalized),
                    unit=self.UNITS[sensor_index % len(self.UNITS)],
                )
            )

        heatmap = self._build_heatmap()
        summary_values = {
            "process_load": float(np.mean(self.current_values)),
            "vent_flow": float(np.percentile(self.current_values, 70)),
            "filter_efficiency": float(np.percentile(self.current_values, 35)),
            "stability_index": float(100.0 - np.std(self.current_values)),
        }
        return Snapshot(
            readings=readings,
            line_history=self.history.copy(),
            heatmap=heatmap,
            summary_values=summary_values,
        )

    def _build_heatmap(self) -> np.ndarray:
        matrix = np.zeros((4, 4), dtype=np.float32)
        for row in range(4):
            for col in range(4):
                sensor_index = (row * 4 + col) % len(self.current_values)
                matrix[row, col] = self.current_values[sensor_index]
        return matrix

    @staticmethod
    def _status_for_value(normalized_value: float) -> str:
        if normalized_value >= 0.84:
            return "ALERT"
        if normalized_value >= 0.68:
            return "WATCH"
        return "STABLE"
