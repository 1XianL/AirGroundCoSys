from __future__ import annotations

from pathlib import Path
import sys


SCRIPT_DIR = Path(__file__).resolve().parent
FEATURE_ROOT = SCRIPT_DIR.parent
if str(FEATURE_ROOT) not in sys.path:
    sys.path.insert(0, str(FEATURE_ROOT))

DEFAULT_CONFIG_PATH = FEATURE_ROOT / "configs" / "example_config.json"
DEFAULT_OUTPUT_PATH = FEATURE_ROOT / "outputs" / "factory_monitoring_demo3.mp4"

from sensor_video_generator.config import load_config
from sensor_video_generator.generator import SensorVideoGenerator

def main() -> None:
    config = load_config(DEFAULT_CONFIG_PATH)
    output_path = DEFAULT_OUTPUT_PATH
    generator = SensorVideoGenerator(config=config)
    generator.generate(output_path)
    print(f"Video written to: {output_path.resolve()}")


if __name__ == "__main__":
    main()
