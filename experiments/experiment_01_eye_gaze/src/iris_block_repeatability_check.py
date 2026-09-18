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

# block_index is intentionally preserved.
BLOCKS = [
    {"block_index": 1, "condition": "CENTER"},
    {"block_index": 2, "condition": "LEFT"},
    {"block_index": 3, "condition": "CENTER"},
    {"block_index": 4, "condition": "RIGHT"},
    {"block_index": 5, "condition": "CENTER"},
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

    return output_dir / f"iris_block_repeatability_{timestamp}.csv"


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("NeuroMirror Experiment 01")
    print("Phase 1D.2C — Block-Level Signal Repeatability")
    print("=" * 70)

    print("\nProtocol:")

    for block in BLOCKS:
        print(
            f"Block {block['block_index']}: "
            f"{block['condition']} "
            f"({CONDITION_DURATION:.0f}s)"
        )

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
        "block_index",
        "condition",
        "condition_elapsed_s",
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

        # ----------------------------------------------------
        # CAMERA WARM-UP
        # ----------------------------------------------------

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
                "NeuroMirror — Block Repeatability",
                frame,
            )

            if cv2.waitKey(1) & 0xFF == 27:
                aborted = True
                break

        # ----------------------------------------------------
        # RECORDING
        # ----------------------------------------------------

        if not aborted:

            experiment_start = time.perf_counter()

            for block in BLOCKS:

                block_index = block["block_index"]
                condition = block["condition"]

                print(
                    f"Block {block_index}/{len(BLOCKS)}: "
                    f"{condition}"
                )

                condition_start = time.perf_counter()

                while True:

                    condition_elapsed = (
                        time.perf_counter()
                        - condition_start
                    )

                    if condition_elapsed >= CONDITION_DURATION:
                        break

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

                        landmarks = (
                            results
                            .multi_face_landmarks[0]
                            .landmark
                        )

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
                            "block_index": block_index,
                            "condition": condition,
                            "condition_elapsed_s": (
                                f"{condition_elapsed:.6f}"
                            ),
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

                    # ------------------------------------------------
                    # DISPLAY
                    # ------------------------------------------------

                    remaining = max(
                        0.0,
                        CONDITION_DURATION - condition_elapsed,
                    )

                    cv2.putText(
                        frame,
                        f"BLOCK {block_index}/5",
                        (30, 45),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (255, 255, 255),
                        2,
                    )

                    cv2.putText(
                        frame,
                        f"LOOK: {condition}",
                        (30, 90),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0,
                        (0, 255, 255),
                        2,
                    )

                    cv2.putText(
                        frame,
                        f"Time: {remaining:.1f}s",
                        (30, 130),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (255, 255, 255),
                        2,
                    )

                    if average_ratio is not None:
                        cv2.putText(
                            frame,
                            f"Iris ratio: {average_ratio:.3f}",
                            (30, 170),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (0, 255, 0),
                            2,
                        )

                    cv2.imshow(
                        "NeuroMirror — Block Repeatability",
                        frame,
                    )

                    if cv2.waitKey(1) & 0xFF == 27:
                        aborted = True
                        break

                if aborted:
                    break

    cap.release()
    cv2.destroyAllWindows()

    # ========================================================
    # SAVE
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

        total_frames = len(rows)

        detected_frames = sum(
            row["face_detected"]
            for row in rows
        )

        detection_rate = (
            detected_frames / total_frames * 100
            if total_frames
            else 0
        )

        print()
        print("=" * 70)
        print("Recording Summary")
        print("=" * 70)
        print(f"Total frames       : {total_frames}")
        print(f"Face detected      : {detected_frames}")
        print(f"Detection rate     : {detection_rate:.2f}%")
        print(f"CSV saved          : {output_path}")

        if aborted:
            print("Status             : ABORTED")
        else:
            print("Status             : COMPLETED")

    else:
        print("No data recorded.")

    print()
    print("Camera released.")


if __name__ == "__main__":
    main()