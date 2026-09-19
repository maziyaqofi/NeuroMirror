import cv2
import mediapipe as mp


# ============================================================
# CONFIGURATION
# ============================================================

CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_FPS = 30


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


# ============================================================
# MAIN DIAGNOSTIC
# ============================================================

def main():

    print(
        "\n=== NeuroMirror Phase 1F.1A "
        "— Vertical Iris Geometry Check ===\n"
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

                    print(
                        f"\r"
                        f"LEFT={left_ratio:.4f} | "
                        f"RIGHT={right_ratio:.4f} | "
                        f"AVG={average_ratio:.4f}",
                        end="",
                        flush=True
                    )

            cv2.imshow(
                "NeuroMirror Vertical Geometry Check",
                frame
            )

            key = cv2.waitKey(1) & 0xFF

            if (
                key == 27
                or key == ord("q")
            ):
                break

    cap.release()

    cv2.destroyAllWindows()

    print(
        "\n\nDiagnostic finished."
    )


if __name__ == "__main__":
    main()