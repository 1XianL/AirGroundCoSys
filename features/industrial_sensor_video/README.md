# Industrial Sensor Video Generator

This standalone feature generates synthetic industrial or environmental monitoring videos at configurable dimensions. The visuals update every 3 seconds and intentionally avoid rendering any timestamps, clocks, dates, or timeline labels.

## Structure

- `sensor_video_generator/`: Python package
- `configs/example_config.json`: example configuration
- `scripts/generate_video.py`: runnable entry point
- `requirements.txt`: minimal dependencies

## Install

```powershell
cd E:\AirGroundCoSys\features\industrial_sensor_video
python -m pip install -r requirements.txt
```

## Generate a video

```powershell
cd E:\AirGroundCoSys\features\industrial_sensor_video
python scripts\generate_video.py --config configs\example_config.json --output outputs\factory_monitoring_demo.mp4
```

## Main configuration fields

- `video.width`: output width in pixels
- `video.height`: output height in pixels
- `video.duration_seconds`: video duration
- `video.fps`: frame rate
- `style.panel_style`: visual theme name
- `simulation.num_sensors`: number of simulated sensors
- `simulation.update_interval_seconds`: data refresh interval, default `3`
- `simulation.value_range`: min and max sensor values
- `simulation.update_behavior`: drift, volatility, and anomaly settings

## Notes

- The generator writes an MP4 file using `imageio`.
- The displayed values change only on each configured update interval so the video behaves like periodic sensor refresh rather than a consumer dashboard.
- Numeric labels and engineering-style status text are allowed, but no time-related text is rendered anywhere in the frames.

## Assumptions and TODO

- Assumption: a synthetic monitoring panel is acceptable for the intended factory inspection simulation use case.
- TODO: add more domain-specific panel presets if later experiments need water treatment, power systems, or warehouse environmental themes.
