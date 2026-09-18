import cv2
import time


CAMERA_INDEX = 0
WIDTH = 1280
HEIGHT = 720
FPS = 30


def main():
    print("=" * 50)
    print("NeuroMirror Experiment 01")
    print("Phase 1B — Camera Preview")
    print("=" * 50)

    camera = cv2.VideoCapture(CAMERA_INDEX)

    if not camera.isOpened():
        print("ERROR: Camera could not be opened.")
        return

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    camera.set(cv2.CAP_PROP_FPS, FPS)

    print("\nCamera opened successfully.")
    print("Press Q to close the preview.")

    frame_count = 0
    start_time = time.perf_counter()
    measured_fps = 0.0

    while True:
        success, frame = camera.read()

        if not success:
            print("ERROR: Failed to read camera frame.")
            break

        frame_count += 1

        elapsed = time.perf_counter() - start_time

        if elapsed >= 1.0:
            measured_fps = frame_count / elapsed
            frame_count = 0
            start_time = time.perf_counter()

        cv2.putText(
            frame,
            f"FPS: {measured_fps:.1f}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            frame,
            "NeuroMirror - Camera Preview",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        cv2.imshow("NeuroMirror Camera Preview", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()

    print("\nCamera released.")
    print("Preview closed.")


if __name__ == "__main__":
    main()
