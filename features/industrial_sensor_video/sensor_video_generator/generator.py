from __future__ import annotations

from pathlib import Path

import imageio.v2 as imageio

from .config import GeneratorConfig
from .rendering import SensorPanelRenderer
from .simulation import SensorDataSimulator


class SensorVideoGenerator:
    """Generates a ready-to-use synthetic monitoring video file."""

    def __init__(self, config: GeneratorConfig) -> None:
        self.config = config
        self.simulator = SensorDataSimulator(config.simulation)
        self.renderer = SensorPanelRenderer(
            width=config.video.width,
            height=config.video.height,
            style_name=config.style.panel_style,
        )

    def generate(self, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        total_frames = self.config.video.duration_seconds * self.config.video.fps
        update_interval_frames = self.config.simulation.update_interval_seconds * self.config.video.fps
        update_interval_frames = max(update_interval_frames, 1)

        current_frame = None
        with imageio.get_writer(output_path, fps=self.config.video.fps, codec="libx264", format="FFMPEG") as writer:
            for frame_index in range(total_frames):
                if frame_index % update_interval_frames == 0 or current_frame is None:
                    snapshot = self.simulator.generate_snapshot()
                    current_frame = self.renderer.render(snapshot)
                writer.append_data(current_frame)
