import cv2
import time

def main():
    print("=" * 50)
    print("NeuroMirror Experiment 01")
    print("Phase 1B — Camera Check")
    print("=" * 50)

    print("\nOpening camera...")

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("ERROR: Camera could not be opened.")
        return

    print("Camera opened successfully.")

    # Request initial capture settings
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    camera.set(cv2.CAP_PROP_FPS, 30)

    width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    requested_fps = 30
    reported_fps = camera.get(cv2.CAP_PROP_FPS)

    print("\nCamera properties:")
    print(f"Resolution     : {width} x {height}")
    print(f"Requested FPS  : {requested_fps}")
    print(f"Reported FPS   : {reported_fps:.2f}")

    print("\nMeasuring actual frame rate...")

    frame_count = 0
    measurement_seconds = 5

    start_time = time.perf_counter()

    while time.perf_counter() - start_time < measurement_seconds:
        success, frame = camera.read()

        if success:
            frame_count += 1

    elapsed = time.perf_counter() - start_time

    measured_fps = frame_count / elapsed

    print(f"Frames captured: {frame_count}")
    print(f"Elapsed time   : {elapsed:.2f} s")
    print(f"Measured FPS   : {measured_fps:.2f}")

    camera.release()

    print("\nCamera released.")
    print("Phase 1B camera check complete.")


if __name__ == "__main__":
    main()