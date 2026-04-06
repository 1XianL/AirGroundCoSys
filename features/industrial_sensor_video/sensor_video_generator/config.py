from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class VideoConfig:
    width: int
    height: int
    duration_seconds: int
    fps: int


@dataclass(frozen=True)
class StyleConfig:
    panel_style: str


@dataclass(frozen=True)
class ValueRange:
    min: float
    max: float


@dataclass(frozen=True)
class UpdateBehaviorConfig:
    drift_strength: float
    volatility: float
    anomaly_probability: float
    spike_scale: float


@dataclass(frozen=True)
class SimulationConfig:
    num_sensors: int
    update_interval_seconds: int
    value_range: ValueRange
    update_behavior: UpdateBehaviorConfig
    seed: int = 0


@dataclass(frozen=True)
class GeneratorConfig:
    video: VideoConfig
    style: StyleConfig
    simulation: SimulationConfig


def load_config(config_path: Path) -> GeneratorConfig:
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    return GeneratorConfig(
        video=VideoConfig(**payload["video"]),
        style=StyleConfig(**payload["style"]),
        simulation=SimulationConfig(
            num_sensors=payload["simulation"]["num_sensors"],
            update_interval_seconds=payload["simulation"].get("update_interval_seconds", 3),
            value_range=ValueRange(**payload["simulation"]["value_range"]),
            update_behavior=UpdateBehaviorConfig(**payload["simulation"]["update_behavior"]),
            seed=payload["simulation"].get("seed", 0),
        ),
    )
