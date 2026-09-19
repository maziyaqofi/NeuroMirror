from pathlib import Path
from datetime import datetime
import csv

import cv2
import mediapipe as mp


# ============================================================
# PHASE 1F.1E
# VERTICAL EYE GEOMETRY QUALITY DIAGNOSTIC
# ============================================================

CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_FPS = 30

RECORDING_DURATION = 10.0


# ============================================================
# MEDIAPIPE LANDMARKS
# ============================================================

LEFT_IRIS_CENTER = 473
RIGHT_IRIS_CENTER = 468

LEFT_UPPER = 386
LEFT_LOWER = 374

RIGHT_UPPER = 159
RIGHT_LOWER = 145


# ============================================================
# OUTPUT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data/raw/development"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# GEOMETRY
# ============================================================

def calculate_vertical_geometry(
    iris_y,
    upper_y,
    lower_y
):
    """
    Calculate raw vertical eye geometry.

    This diagnostic intentionally preserves the
    components used to construct the normalized
    vertical iris ratio.

    No smoothing, filtering, clipping, or quality
    rejection is applied here.
    """

    y_min = min(
        upper_y,
        lower_y
    )

    y_max = max(
        upper_y,
        lower_y
    )

    eye_aperture = (
        y_max - y_min
    )

    if eye_aperture <= 0:
        return (
            None,
            eye_aperture
        )

    vertical_ratio = (
        (iris_y - y_min)
        / eye_aperture
    )

    return (
        vertical_ratio,
        eye_aperture
    )

# ============================================================
# ACQUISITION
# ============================================================

def run_geometry_diagnostic():

    cap = cv2.VideoCapture(
        CAMERA_INDEX
    )

    cap.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        CAMERA_WIDTH
    )

    cap.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        CAMERA_HEIGHT
    )

    cap.set(
        cv2.CAP_PROP_FPS,
        CAMERA_FPS
    )

    if not cap.isOpened():
        raise RuntimeError(
            "Could not open camera."
        )

    mp_face_mesh = (
        mp.solutions.face_mesh
    )

    rows = []

    start_time = (
        cv2.getTickCount()
        / cv2.getTickFrequency()
    )

    frame_number = 0

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
                continue

            timestamp = (
                cv2.getTickCount()
                / cv2.getTickFrequency()
            )

            elapsed = (
                timestamp - start_time
            )

            if elapsed >= RECORDING_DURATION:
                break

            frame_number += 1

            rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            results = face_mesh.process(
                rgb
            )

            row = {
                "timestamp": elapsed,
                "frame_number": frame_number,
                "face_detected": 0,

                "left_iris_y": None,
                "left_upper_y": None,
                "left_lower_y": None,
                "left_eye_aperture": None,
                "left_vertical_ratio": None,

                "right_iris_y": None,
                "right_upper_y": None,
                "right_lower_y": None,
                "right_eye_aperture": None,
                "right_vertical_ratio": None,
            }

            if results.multi_face_landmarks:

                landmarks = (
                    results
                    .multi_face_landmarks[0]
                    .landmark
                )

                row["face_detected"] = 1

                # --------------------------------------------
                # LEFT EYE
                # --------------------------------------------

                left_iris_y = (
                    landmarks[
                        LEFT_IRIS_CENTER
                    ].y
                )

                left_upper_y = (
                    landmarks[
                        LEFT_UPPER
                    ].y
                )

                left_lower_y = (
                    landmarks[
                        LEFT_LOWER
                    ].y
                )

                (
                    left_ratio,
                    left_aperture
                ) = calculate_vertical_geometry(
                    left_iris_y,
                    left_upper_y,
                    left_lower_y
                )

                row.update({
                    "left_iris_y": left_iris_y,
                    "left_upper_y": left_upper_y,
                    "left_lower_y": left_lower_y,
                    "left_eye_aperture": left_aperture,
                    "left_vertical_ratio": left_ratio,
                })

                # --------------------------------------------
                # RIGHT EYE
                # --------------------------------------------

                right_iris_y = (
                    landmarks[
                        RIGHT_IRIS_CENTER
                    ].y
                )

                right_upper_y = (
                    landmarks[
                        RIGHT_UPPER
                    ].y
                )

                right_lower_y = (
                    landmarks[
                        RIGHT_LOWER
                    ].y
                )

                (
                    right_ratio,
                    right_aperture
                ) = calculate_vertical_geometry(
                    right_iris_y,
                    right_upper_y,
                    right_lower_y
                )

                row.update({
                    "right_iris_y": right_iris_y,
                    "right_upper_y": right_upper_y,
                    "right_lower_y": right_lower_y,
                    "right_eye_aperture": right_aperture,
                    "right_vertical_ratio": right_ratio,
                })

            rows.append(
                row
            )

    cap.release()

    return rows

# ============================================================
# RAW DATA SAVING
# ============================================================

def save_geometry_data(rows):

    run_timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    output_path = (
        OUTPUT_DIR
        / f"vertical_eye_geometry_quality_{run_timestamp}.csv"
    )

    fieldnames = [
        "timestamp",
        "frame_number",
        "face_detected",

        "left_iris_y",
        "left_upper_y",
        "left_lower_y",
        "left_eye_aperture",
        "left_vertical_ratio",

        "right_iris_y",
        "right_upper_y",
        "right_lower_y",
        "right_eye_aperture",
        "right_vertical_ratio",
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
        writer.writerows(rows)

    return output_path


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n=== NeuroMirror Phase 1F.1E "
        "— Vertical Eye Geometry Quality Diagnostic ===\n"
    )

    print(
        f"Recording duration : "
        f"{RECORDING_DURATION:.1f} s"
    )

    print(
        "Instruction        : "
        "Look naturally toward the center "
        "and keep your head still."
    )

    print(
        "\nStarting recording...\n"
    )

    rows = run_geometry_diagnostic()

    total_samples = len(rows)

    face_samples = sum(
        row["face_detected"]
        for row in rows
    )

    if total_samples > 0:

        face_rate = (
            face_samples
            / total_samples
            * 100.0
        )

    else:

        face_rate = 0.0

    output_path = save_geometry_data(
        rows
    )

    print(
        "=== RUN SUMMARY ==="
    )

    print(
        f"Total samples       : "
        f"{total_samples}"
    )

    print(
        f"Face detected       : "
        f"{face_samples}"
    )

    print(
        f"Face detection rate : "
        f"{face_rate:.1f}%"
    )

    print(
        "\nRaw geometry saved:"
    )

    print(
        f"  {output_path}"
    )

    print(
        "\nVertical eye geometry "
        "diagnostic finished."
    )


if __name__ == "__main__":
    main()