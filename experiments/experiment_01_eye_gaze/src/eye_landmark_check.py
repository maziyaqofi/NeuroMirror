import cv2
import mediapipe as mp


CAMERA_INDEX = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# MediaPipe Face Mesh landmark indices
LEFT_IRIS = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]


def main():
    print("=" * 55)
    print("NeuroMirror Experiment 01")
    print("Phase 1D.1D — Eye/Iris Landmark Detection Check")
    print("=" * 55)

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

                # Draw all facial landmarks
                for landmark in face_landmarks.landmark:
                    x = int(landmark.x * actual_width)
                    y = int(landmark.y * actual_height)

                    cv2.circle(
                        frame,
                        (x, y),
                        1,
                        (0, 255, 0),
                        -1,
                    )

                # Highlight iris landmarks
                for index in LEFT_IRIS + RIGHT_IRIS:
                    landmark = face_landmarks.landmark[index]

                    x = int(landmark.x * actual_width)
                    y = int(landmark.y * actual_height)

                    cv2.circle(
                        frame,
                        (x, y),
                        3,
                        (0, 0, 255),
                        -1,
                    )

                cv2.putText(
                    frame,
                    "FACE + IRIS DETECTED",
                    (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2,
                )

            else:
                cv2.putText(
                    frame,
                    "NO FACE DETECTED",
                    (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2,
                )

            cv2.imshow("NeuroMirror — Eye Landmark Check", frame)

            key = cv2.waitKey(1) & 0xFF

            if key == 27:  # ESC
                break

    cap.release()
    cv2.destroyAllWindows()

    print()
    print("Camera released.")
    print("Eye/Iris landmark detection check complete.")


if __name__ == "__main__":
    main()