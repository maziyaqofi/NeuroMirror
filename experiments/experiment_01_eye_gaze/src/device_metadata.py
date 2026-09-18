import cv2
import json
import platform
import subprocess
import re
import sys
import time
from datetime import datetime
from pathlib import Path


CAMERA_INDEX = 0
REQUESTED_WIDTH = 1280
REQUESTED_HEIGHT = 720
REQUESTED_FPS = 30
FPS_MEASUREMENT_SECONDS = 5


def get_system_info():
    return {
        "operating_system": platform.system(),
        "os_release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
    }


def get_display_info():
    try:
        result = subprocess.run(
            ["system_profiler", "SPDisplaysDataType"],
            capture_output=True,
            text=True,
            check=True
        )

        match = re.search(
            r"Resolution:\s+(\d+)\s+x\s+(\d+)",
            result.stdout
        )

        if match:
            width = int(match.group(1))
            height = int(match.group(2))

            return {
                "detected": True,
                "physical_width_px": width,
                "physical_height_px": height,
                "aspect_ratio": round(width / height, 3)
            }

    except Exception as error:
        return {
            "detected": False,
            "error": str(error)
        }

    return {
        "detected": False,
        "error": "Display resolution could not be parsed."
    }


def get_camera_info():
    camera = cv2.VideoCapture(CAMERA_INDEX)

    if not camera.isOpened():
        return {
            "detected": False,
            "error": "Camera could not be opened."
        }

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, REQUESTED_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, REQUESTED_HEIGHT)
    camera.set(cv2.CAP_PROP_FPS, REQUESTED_FPS)

    width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    reported_fps = camera.get(cv2.CAP_PROP_FPS)

    frame_count = 0
    start_time = time.perf_counter()

    while time.perf_counter() - start_time < FPS_MEASUREMENT_SECONDS:
        success, _ = camera.read()

        if success:
            frame_count += 1

    elapsed = time.perf_counter() - start_time
    measured_fps = frame_count / elapsed if elapsed > 0 else 0

    camera.release()

    return {
        "detected": True,
        "camera_index": CAMERA_INDEX,

        "requested_resolution": {
            "width": REQUESTED_WIDTH,
            "height": REQUESTED_HEIGHT
        },

        "actual_resolution": {
            "width": width,
            "height": height
        },

        "requested_fps": REQUESTED_FPS,
        "reported_fps": round(reported_fps, 2),
        "measured_fps": round(measured_fps, 2),

        "measurement_duration_seconds": round(elapsed, 2),
        "frames_captured": frame_count
    }


def main():
    print("=" * 50)
    print("NeuroMirror Experiment 01")
    print("Phase 1B — Device Metadata")
    print("=" * 50)

    print("\nCollecting system information...")
    system_info = get_system_info()

    print("Detecting display...")
    display_info = get_display_info()

    print("Testing camera...")
    camera_info = get_camera_info()

    metadata = {
        "project": "NeuroMirror",
        "experiment": "Experiment 01",
        "metadata_type": "device_environment",
        "generated_at": datetime.now().astimezone().isoformat(),

        "system": system_info,
        "display": display_info,
        "camera": camera_info
    }

    project_root = Path(__file__).resolve().parents[3]

    output_directory = project_root / "data"
    output_directory.mkdir(parents=True, exist_ok=True)

    output_file = output_directory / "device_metadata.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=4)

    print("\nDevice metadata successfully generated.")
    print(f"Saved to: {output_file}")

    print("\nSummary:")
    print(f"Python       : {system_info['python_version']}")
    print(f"Architecture : {system_info['machine']}")

    if display_info["detected"]:
        print(
            f"Display      : "
            f"{display_info['physical_width_px']} x "
            f"{display_info['physical_height_px']}"
        )

    if camera_info["detected"]:
        print(
            f"Camera       : "
            f"{camera_info['actual_resolution']['width']} x "
            f"{camera_info['actual_resolution']['height']}"
        )

        print(
            f"Measured FPS : "
            f"{camera_info['measured_fps']}"
        )

    print("\nPhase 1B device metadata complete.")


if __name__ == "__main__":
    main()