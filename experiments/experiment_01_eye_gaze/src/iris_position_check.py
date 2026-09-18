import cv2
import mediapipe as mp


CAMERA_INDEX = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# MediaPipe Face Mesh landmarks
# Iris centers
RIGHT_IRIS_CENTER = 468
LEFT_IRIS_CENTER = 473

# Eye corners
RIGHT_EYE_OUTER = 33
RIGHT_EYE_INNER = 133

LEFT_EYE_INNER = 362
LEFT_EYE_OUTER = 263


def normalized_horizontal_position(landmarks, iris_idx, corner_a_idx, corner_b_idx):
    """
    Calculate horizontal iris position relative to the two eye corners.

    Returns approximately:
        0.0 -> near one eye corner
        0.5 -> near center
        1.0 -> near opposite eye corner

    We do NOT label these as gaze-left/right yet.
    """

    iris_x = landmarks[iris_idx].x
    corner_a_x = landmarks[corner_a_idx].x
    corner_b_x = landmarks[corner_b_idx].x

    x_min = min(corner_a_x, corner_b_x)
    x_max = max(corner_a_x, corner_b_x)

    eye_width = x_max - x_min

    if eye_width <= 0:
        return None

    return (iris_x - x_min) / eye_width


def main():
    print("=" * 60)
    print("NeuroMirror Experiment 01")
    print("Phase 1D.2A — Normalized Iris Position Signal")
    print("=" * 60)

    cap = cv2.VideoCapture(CAMERA_INDEX)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, 30)

    if not cap.isOpened():
        print("ERROR: Could not open camera.")
        return

    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    reported_fps = cap.get(cv2.CAP_PROP_FPS)

    print("Camera opened successfully.")
    print(f"Resolution   : {actual_width} x {actual_height}")
    print(f"Reported FPS : {reported_fps:.2f}")
    print()
    print("Keep your head as still as possible.")
    print("Test: LEFT -> CENTER -> RIGHT")
    print("Press ESC to exit.")

    mp_face_mesh = mp.solutions.face_mesh

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
                print("WARNING: Failed to capture frame.")
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_frame)

            if results.multi_face_landmarks:

                face_landmarks = results.multi_face_landmarks[0]
                landmarks = face_landmarks.landmark

                right_ratio = normalized_horizontal_position(
                    landmarks,
                    RIGHT_IRIS_CENTER,
                    RIGHT_EYE_OUTER,
                    RIGHT_EYE_INNER,
                )

                left_ratio = normalized_horizontal_position(
                    landmarks,
                    LEFT_IRIS_CENTER,
                    LEFT_EYE_INNER,
                    LEFT_EYE_OUTER,
                )

                if right_ratio is not None and left_ratio is not None:

                    average_ratio = (right_ratio + left_ratio) / 2.0

                    text_right = f"RIGHT EYE : {right_ratio:.3f}"
                    text_left = f"LEFT EYE  : {left_ratio:.3f}"
                    text_avg = f"AVERAGE   : {average_ratio:.3f}"

                    cv2.putText(
                        frame,
                        text_right,
                        (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2,
                    )

                    cv2.putText(
                        frame,
                        text_left,
                        (30, 75),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2,
                    )

                    cv2.putText(
                        frame,
                        text_avg,
                        (30, 110),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 255),
                        2,
                    )

                    # Draw iris centers
                    for iris_idx in [RIGHT_IRIS_CENTER, LEFT_IRIS_CENTER]:

                        landmark = landmarks[iris_idx]

                        x = int(landmark.x * actual_width)
                        y = int(landmark.y * actual_height)

                        cv2.circle(
                            frame,
                            (x, y),
                            4,
                            (0, 0, 255),
                            -1,
                        )

            else:
                cv2.putText(
                    frame,
                    "NO FACE DETECTED",
                    (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                )

            cv2.imshow(
                "NeuroMirror — Normalized Iris Position",
                frame,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == 27:
                break

    cap.release()
    cv2.destroyAllWindows()

    print()
    print("Camera released.")
    print("Normalized iris position check complete.")


if __name__ == "__main__":
    main()