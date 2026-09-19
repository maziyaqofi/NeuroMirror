import csv
from pathlib import Path
from datetime import datetime

import cv2
import mediapipe as mp


CAMERA_INDEX = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
CAMERA_FPS = 30

RECORDING_DURATION = 10.0

PROJECT_ROOT = Path(__file__).resolve().parents[3]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "development"
)


# ============================================================
# MEDIAPIPE LANDMARKS
# ============================================================

RIGHT_IRIS_CENTER = 468
LEFT_IRIS_CENTER = 473

RIGHT_EYE_OUTER = 33
RIGHT_EYE_INNER = 133

LEFT_EYE_INNER = 362
LEFT_EYE_OUTER = 263


# ============================================================
# EYE GEOMETRY
# ============================================================

def extract_eye_geometry(
    landmarks,
    iris_idx,
    corner_a_idx,
    corner_b_idx,
):
    iris_x = landmarks[iris_idx].x
    corner_a_x = landmarks[corner_a_idx].x
    corner_b_x = landmarks[corner_b_idx].x

    x_min = min(
        corner_a_x,
        corner_b_x,
    )

    x_max = max(
        corner_a_x,
        corner_b_x,
    )

    eye_width = (
        x_max - x_min
    )

    if eye_width <= 0:
        ratio = None
    else:
        ratio = (
            iris_x - x_min
        ) / eye_width

    return {
        "iris_x": iris_x,
        "corner_a_x": corner_a_x,
        "corner_b_x": corner_b_x,
        "x_min": x_min,
        "x_max": x_max,
        "eye_width": eye_width,
        "ratio": ratio,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n=== NeuroMirror 1D.5C "
        "— Raw Eye Geometry Stability ===\n"
    )

    print(
        "Instruction:"
    )

    print(
        "Look at the CENTER of the screen "
        "and keep your head as still as possible."
    )

    print(
        f"Recording duration: "
        f"{RECORDING_DURATION:.0f} seconds\n"
    )

    cap = cv2.VideoCapture(
        CAMERA_INDEX
    )

    cap.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        FRAME_WIDTH
    )

    cap.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        FRAME_HEIGHT
    )

    cap.set(
        cv2.CAP_PROP_FPS,
        CAMERA_FPS
    )

    if not cap.isOpened():

        print(
            "ERROR: Could not open camera."
        )

        return

    actual_width = int(
        cap.get(
            cv2.CAP_PROP_FRAME_WIDTH
        )
    )

    actual_height = int(
        cap.get(
            cv2.CAP_PROP_FRAME_HEIGHT
        )
    )

    reported_fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    print(
        f"Resolution   : "
        f"{actual_width} x "
        f"{actual_height}"
    )

    print(
        f"Reported FPS : "
        f"{reported_fps:.2f}\n"
    )

    mp_face_mesh = (
        mp.solutions.face_mesh
    )

    samples = []

    frame_number = 0

    start_tick = (
        cv2.getTickCount()
    )

    tick_frequency = (
        cv2.getTickFrequency()
    )

    with mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as face_mesh:

        while True:

            success, frame = cap.read()

            if not success:

                print(
                    "WARNING: "
                    "Failed to capture frame."
                )

                break

            current_tick = (
                cv2.getTickCount()
            )

            elapsed = (
                current_tick
                - start_tick
            ) / tick_frequency

            if elapsed >= RECORDING_DURATION:
                break

            frame_number += 1

            rgb_frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            results = face_mesh.process(
                rgb_frame
            )

            row = {
                "timestamp": elapsed,
                "frame_number": frame_number,
                "face_detected": 0,

                "left_iris_x": None,
                "left_corner_a_x": None,
                "left_corner_b_x": None,
                "left_eye_width": None,
                "left_iris_ratio": None,

                "right_iris_x": None,
                "right_corner_a_x": None,
                "right_corner_b_x": None,
                "right_eye_width": None,
                "right_iris_ratio": None,

                "average_iris_ratio": None,
            }

            if results.multi_face_landmarks:

                row[
                    "face_detected"
                ] = 1

                landmarks = (
                    results
                    .multi_face_landmarks[0]
                    .landmark
                )

                left = extract_eye_geometry(
                    landmarks,
                    LEFT_IRIS_CENTER,
                    LEFT_EYE_INNER,
                    LEFT_EYE_OUTER,
                )

                right = extract_eye_geometry(
                    landmarks,
                    RIGHT_IRIS_CENTER,
                    RIGHT_EYE_OUTER,
                    RIGHT_EYE_INNER,
                )

                row.update({
                    "left_iris_x":
                        left["iris_x"],

                    "left_corner_a_x":
                        left["corner_a_x"],

                    "left_corner_b_x":
                        left["corner_b_x"],

                    "left_eye_width":
                        left["eye_width"],

                    "left_iris_ratio":
                        left["ratio"],

                    "right_iris_x":
                        right["iris_x"],

                    "right_corner_a_x":
                        right["corner_a_x"],

                    "right_corner_b_x":
                        right["corner_b_x"],

                    "right_eye_width":
                        right["eye_width"],

                    "right_iris_ratio":
                        right["ratio"],
                })

                if (
                    left["ratio"] is not None
                    and
                    right["ratio"] is not None
                ):

                    row[
                        "average_iris_ratio"
                    ] = (
                        left["ratio"]
                        + right["ratio"]
                    ) / 2.0

            samples.append(row)

    cap.release()

    # ========================================================
    # SAVE
    # ========================================================

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp_string = (
        datetime.now()
        .strftime("%Y%m%d_%H%M%S")
    )

    output_path = (
        OUTPUT_DIR
        / (
            "eye_geometry_stability_"
            f"{timestamp_string}.csv"
        )
    )

    fieldnames = [
        "timestamp",
        "frame_number",
        "face_detected",

        "left_iris_x",
        "left_corner_a_x",
        "left_corner_b_x",
        "left_eye_width",
        "left_iris_ratio",

        "right_iris_x",
        "right_corner_a_x",
        "right_corner_b_x",
        "right_eye_width",
        "right_iris_ratio",

        "average_iris_ratio",
    ]

    with output_path.open(
        "w",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(
            samples
        )

    total_samples = len(
        samples
    )

    detected_samples = sum(
        sample["face_detected"]
        for sample in samples
    )

    detection_rate = (
        detected_samples
        / total_samples
        * 100
        if total_samples
        else 0.0
    )

    print(
        "=" * 55
    )

    print(
        "Status              : "
        "COMPLETED"
    )

    print(
        f"Samples             : "
        f"{total_samples}"
    )

    print(
        f"Face detected       : "
        f"{detected_samples}"
    )

    print(
        f"Face detection rate : "
        f"{detection_rate:.2f}%"
    )

    print(
        f"\nOutput file : "
        f"{output_path}"
    )

    print(
        "=" * 55
    )


if __name__ == "__main__":
    main()