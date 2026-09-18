import csv
import time
from datetime import datetime
from pathlib import Path

import cv2
import mediapipe as mp


# ============================================================
# CONFIGURATION
# ============================================================

CAMERA_INDEX = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
REQUESTED_FPS = 30

CONDITION_DURATION = 5.0

# Sequence intentionally returns to CENTER between directions.
CONDITIONS = [
    "CENTER",
    "LEFT",
    "CENTER",
    "RIGHT",
    "CENTER",
]

# MediaPipe Face Mesh landmark indices
RIGHT_IRIS_CENTER = 468
LEFT_IRIS_CENTER = 473

RIGHT_EYE_OUTER = 33
RIGHT_EYE_INNER = 133

LEFT_EYE_INNER = 362
LEFT_EYE_OUTER = 263


# ============================================================
# HELPERS
# ============================================================

def normalized_horizontal_position(
    landmarks,
    iris_idx,
    corner_a_idx,
    corner_b_idx,
):
    iris_x = landmarks[iris_idx].x
    corner_a_x = landmarks[corner_a_idx].x
    corner_b_x = landmarks[corner_b_idx].x

    x_min = min(corner_a_x, corner_b_x)
    x_max = max(corner_a_x, corner_b_x)

    eye_width = x_max - x_min

    if eye_width <= 0:
        return None

    return (iris_x - x_min) / eye_width


def get_output_path():
    project_root = Path(__file__).resolve().parents[3]

    output_dir = (
        project_root
        / "data"
        / "raw"
        / "development"
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    return output_dir / f"iris_signal_{timestamp}.csv"


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 65)
    print("NeuroMirror Experiment 01")
    print("Phase 1D.2B — Automatic Iris Signal Recording")
    print("=" * 65)

    print()
    print("Protocol:")
    print("CENTER -> LEFT -> CENTER -> RIGHT -> CENTER")
    print(f"{CONDITION_DURATION:.0f} seconds per condition.")
    print()
    print("Keep your head as still as possible.")
    print("Move your eyes only.")
    print("Press ESC to abort.")
    print()

    output_path = get_output_path()

    cap = cv2.VideoCapture(CAMERA_INDEX)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, REQUESTED_FPS)

    if not cap.isOpened():
        print("ERROR: Could not open camera.")
        return

    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    reported_fps = cap.get(cv2.CAP_PROP_FPS)

    print("Camera opened successfully.")
    print(f"Resolution    : {actual_width} x {actual_height}")
    print(f"Reported FPS  : {reported_fps:.2f}")
    print(f"Output        : {output_path}")
    print()

    fieldnames = [
        "timestamp",
        "frame_number",
        "condition",
        "left_iris_ratio",
        "right_iris_ratio",
        "average_iris_ratio",
        "face_detected",
    ]

    rows = []

    frame_number = 0
    aborted = False

    mp_face_mesh = mp.solutions.face_mesh

    with mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as face_mesh:

        # Give the camera and tracker a short warm-up.
        print("Camera warm-up...")
        warmup_start = time.perf_counter()

        while time.perf_counter() - warmup_start < 2.0:
            success, frame = cap.read()

            if not success:
                continue

            cv2.putText(
                frame,
                "GET READY",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 255),
                2,
            )

            cv2.imshow(
                "NeuroMirror — Iris Signal Recording",
                frame,
            )

            if cv2.waitKey(1) & 0xFF == 27:
                aborted = True
                break

        if not aborted:
            experiment_start = time.perf_counter()

            for condition_index, condition in enumerate(CONDITIONS):

                print(
                    f"Condition {condition_index + 1}/{len(CONDITIONS)}: "
                    f"{condition}"
                )

                condition_start = time.perf_counter()

                while (
                    time.perf_counter() - condition_start
                    < CONDITION_DURATION
                ):
                    success, frame = cap.read()

                    if not success:
                        continue

                    frame_number += 1

                    timestamp = (
                        time.perf_counter()
                        - experiment_start
                    )

                    rgb_frame = cv2.cvtColor(
                        frame,
                        cv2.COLOR_BGR2RGB,
                    )

                    results = face_mesh.process(rgb_frame)

                    face_detected = 0

                    left_ratio = None
                    right_ratio = None
                    average_ratio = None

                    if results.multi_face_landmarks:

                        face_detected = 1

                        face_landmarks = (
                            results.multi_face_landmarks[0]
                        )

                        landmarks = face_landmarks.landmark

                        right_ratio = (
                            normalized_horizontal_position(
                                landmarks,
                                RIGHT_IRIS_CENTER,
                                RIGHT_EYE_OUTER,
                                RIGHT_EYE_INNER,
                            )
                        )

                        left_ratio = (
                            normalized_horizontal_position(
                                landmarks,
                                LEFT_IRIS_CENTER,
                                LEFT_EYE_INNER,
                                LEFT_EYE_OUTER,
                            )
                        )

                        if (
                            right_ratio is not None
                            and left_ratio is not None
                        ):
                            average_ratio = (
                                right_ratio + left_ratio
                            ) / 2.0

                    rows.append(
                        {
                            "timestamp": f"{timestamp:.6f}",
                            "frame_number": frame_number,
                            "condition": condition,
                            "left_iris_ratio": (
                                f"{left_ratio:.6f}"
                                if left_ratio is not None
                                else ""
                            ),
                            "right_iris_ratio": (
                                f"{right_ratio:.6f}"
                                if right_ratio is not None
                                else ""
                            ),
                            "average_iris_ratio": (
                                f"{average_ratio:.6f}"
                                if average_ratio is not None
                                else ""
                            ),
                            "face_detected": face_detected,
                        }
                    )

                    # ----------------------------------------
                    # DISPLAY
                    # ----------------------------------------

                    cv2.putText(
                        frame,
                        f"LOOK: {condition}",
                        (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0,
                        (0, 255, 255),
                        2,
                    )

                    elapsed_condition = (
                        time.perf_counter()
                        - condition_start
                    )

                    remaining = max(
                        0.0,
                        CONDITION_DURATION - elapsed_condition,
                    )

                    cv2.putText(
                        frame,
                        f"Time: {remaining:.1f}s",
                        (30, 90),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (255, 255, 255),
                        2,
                    )

                    if average_ratio is not None:
                        cv2.putText(
                            frame,
                            f"Iris ratio: {average_ratio:.3f}",
                            (30, 130),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (0, 255, 0),
                            2,
                        )

                    cv2.imshow(
                        "NeuroMirror — Iris Signal Recording",
                        frame,
                    )

                    key = cv2.waitKey(1) & 0xFF

                    if key == 27:
                        aborted = True
                        break

                if aborted:
                    break

    cap.release()
    cv2.destroyAllWindows()

    # ========================================================
    # SAVE CSV
    # ========================================================

    if rows:
        with open(
            output_path,
            "w",
            newline="",
            encoding="utf-8",
        ) as csvfile:

            writer = csv.DictWriter(
                csvfile,
                fieldnames=fieldnames,
            )

            writer.writeheader()
            writer.writerows(rows)

        detected_frames = sum(
            row["face_detected"] for row in rows
        )

        total_frames = len(rows)

        detection_rate = (
            detected_frames / total_frames * 100
            if total_frames > 0
            else 0
        )

        print()
        print("=" * 65)
        print("Recording Summary")
        print("=" * 65)
        print(f"Total frames       : {total_frames}")
        print(f"Face detected      : {detected_frames}")
        print(f"Detection rate     : {detection_rate:.2f}%")
        print(f"CSV saved          : {output_path}")

        if aborted:
            print("Status             : ABORTED")
        else:
            print("Status             : COMPLETED")

    else:
        print()
        print("No data recorded.")

    print()
    print("Camera released.")


if __name__ == "__main__":
    main()