import cv2
import mediapipe as mp
import statistics

# ============================================================
# CONFIGURATION
# ============================================================

CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_FPS = 30

CONDITION_DURATION = 5.0

CONDITIONS = [
    "CENTER",
    "TOP",
    "CENTER_REPEAT",
    "BOTTOM",
]

# ============================================================
# MEDIAPIPE LANDMARK CONFIGURATION
# ============================================================

# Iris centers
LEFT_IRIS_CENTER = 473
RIGHT_IRIS_CENTER = 468

# Candidate vertical eyelid anchors
LEFT_EYE_UPPER = 386
LEFT_EYE_LOWER = 374

RIGHT_EYE_UPPER = 159
RIGHT_EYE_LOWER = 145


# ============================================================
# HELPERS
# ============================================================

def normalized_vertical_position(
    iris_y,
    upper_y,
    lower_y
):
    """
    Calculate iris vertical position relative to the
    upper and lower eyelid landmarks.

    This is an experimental geometry signal only.
    It is not yet a calibrated gaze estimate.
    """

    y_min = min(
        upper_y,
        lower_y
    )

    y_max = max(
        upper_y,
        lower_y
    )

    height = y_max - y_min

    if height <= 0:
        return None

    return (
        (iris_y - y_min)
        / height
    )

def summarize_condition(
    condition,
    left_samples,
    right_samples,
    average_samples
):
    """
    Print a robust summary for one controlled
    vertical gaze condition.
    """

    if not average_samples:
        print(
            f"\n{condition}: "
            "No valid samples collected."
        )
        return

    left_median = statistics.median(
        left_samples
    )

    right_median = statistics.median(
        right_samples
    )

    average_median = statistics.median(
        average_samples
    )

    print(
        f"\n{condition}"
        f"\n  Samples      : {len(average_samples)}"
        f"\n  LEFT median  : {left_median:.4f}"
        f"\n  RIGHT median : {right_median:.4f}"
        f"\n  AVG median   : {average_median:.4f}"
    )

# ============================================================
# MAIN DIAGNOSTIC
# ============================================================

def main():

    print(
        "\n=== NeuroMirror Phase 1F.1B "
        "— Controlled Vertical Iris Direction Check ===\n"
    )

    print(
        "Conditions:"
        "\n  CENTER"
        "\n  TOP"
        "\n  CENTER_REPEAT"
        "\n  BOTTOM"
        f"\n\nEach condition will be recorded for "
        f"{CONDITION_DURATION:.1f} seconds."
    )

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

    mp_face_mesh = (
        mp.solutions.face_mesh
    )

    condition_results = {}

    with mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as face_mesh:

        for condition in CONDITIONS:

            # ========================================================
            # PREPARATION / CAMERA PREVIEW
            # ========================================================

            print(
                f"\n\nPrepare for: {condition}"
            )

            print(
                "Camera preview is active."
                "\nLook at the requested position."
                "\nPress SPACE in the camera window to start recording."
                "\nPress Q or ESC to abort."
            )

            while True:

                success, frame = cap.read()

                if not success:
                    continue

                cv2.putText(
                    frame,
                    f"Prepare: {condition}",
                    (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA
                )

                cv2.putText(
                    frame,
                    "SPACE = start | Q / ESC = abort",
                    (30, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA
                )

                cv2.imshow(
                    "NeuroMirror Vertical Direction Check",
                    frame
                )

                key = cv2.waitKey(1) & 0xFF

                if key == ord(" "):
                    break

                if (
                    key == 27
                    or key == ord("q")
                ):
                    cap.release()
                    cv2.destroyAllWindows()

                    print(
                        "\nDiagnostic aborted."
                    )

                    return

            # ========================================================
            # CONDITION RECORDING
            # ========================================================

            left_samples = []
            right_samples = []
            average_samples = []

            start_time = cv2.getTickCount()

            while True:

                elapsed = (
                    (
                        cv2.getTickCount()
                        - start_time
                    )
                    / cv2.getTickFrequency()
                )

                if elapsed >= CONDITION_DURATION:
                    break

                success, frame = cap.read()

                if not success:
                    continue

                rgb = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2RGB
                )

                results = face_mesh.process(
                    rgb
                )

                if results.multi_face_landmarks:

                    landmarks = (
                        results
                        .multi_face_landmarks[0]
                        .landmark
                    )

                    left_ratio = (
                        normalized_vertical_position(
                            landmarks[
                                LEFT_IRIS_CENTER
                            ].y,
                            landmarks[
                                LEFT_EYE_UPPER
                            ].y,
                            landmarks[
                                LEFT_EYE_LOWER
                            ].y,
                        )
                    )

                    right_ratio = (
                        normalized_vertical_position(
                            landmarks[
                                RIGHT_IRIS_CENTER
                            ].y,
                            landmarks[
                                RIGHT_EYE_UPPER
                            ].y,
                            landmarks[
                                RIGHT_EYE_LOWER
                            ].y,
                        )
                    )

                    if (
                        left_ratio is not None
                        and right_ratio is not None
                    ):

                        average_ratio = (
                            left_ratio
                            + right_ratio
                        ) / 2.0

                        left_samples.append(
                            left_ratio
                        )

                        right_samples.append(
                            right_ratio
                        )

                        average_samples.append(
                            average_ratio
                        )

                        print(
                            f"\r"
                            f"{condition:13s} | "
                            f"LEFT={left_ratio:.4f} | "
                            f"RIGHT={right_ratio:.4f} | "
                            f"AVG={average_ratio:.4f} | "
                            f"t={elapsed:.1f}s",
                            end="",
                            flush=True
                        )

                cv2.putText(
                    frame,
                    f"RECORDING: {condition}",
                    (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA
                )

                cv2.putText(
                    frame,
                    f"Time: {elapsed:.1f} / {CONDITION_DURATION:.1f}s",
                    (30, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA
                )

                cv2.imshow(
                    "NeuroMirror Vertical Direction Check",
                    frame
                )

                key = cv2.waitKey(1) & 0xFF

                if (
                    key == 27
                    or key == ord("q")
                ):
                    cap.release()
                    cv2.destroyAllWindows()

                    print(
                        "\n\nDiagnostic aborted."
                    )

                    return

            # ========================================================
            # CONDITION SUMMARY
            # ========================================================

            summarize_condition(
                condition,
                left_samples,
                right_samples,
                average_samples
            )

            if average_samples:

                condition_results[
                    condition
                ] = {
                    "sample_count": len(
                        average_samples
                    ),
                    "left_median": statistics.median(
                        left_samples
                    ),
                    "right_median": statistics.median(
                        right_samples
                    ),
                    "average_median": statistics.median(
                        average_samples
                    ),
                }

    cap.release()

    cv2.destroyAllWindows()

    print(
        "\n\n=== CONDITION SUMMARY ==="
    )

    for condition in CONDITIONS:

        result = condition_results.get(
            condition
        )

        if result is None:
            print(
                f"{condition:13s}: "
                "NO VALID DATA"
            )
            continue

        print(
            f"{condition:13s}: "
            f"N={result['sample_count']:3d} | "
            f"LEFT={result['left_median']:.4f} | "
            f"RIGHT={result['right_median']:.4f} | "
            f"AVG={result['average_median']:.4f}"
        )

    print(
        "\nDiagnostic finished."
    )


if __name__ == "__main__":
    main()