"""
NeuroMirror Phase 1F.3A
Independent Calibration Validation Acquisition

Purpose
-------
Acquire synchronized eye-geometry measurements from validation
targets that were not used to fit the 9-point calibration model.

The validation targets lie inside the calibrated visual region
and are intended to evaluate interpolation to unseen positions.

Validation data must not be used to refit or tune the
calibration model.

This is a development diagnostic only.
"""

from pathlib import Path
import csv
from datetime import datetime
import threading

import cv2
import mediapipe as mp

from psychopy import visual, core, monitors


# ============================================================
# CONFIGURATION
# ============================================================

MONITOR_NAME = "neuromirror_macbook"
WINDOW_SIZE = (1440, 900)

CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_FPS = 30

TARGET_DURATION = 2.0

OUTPUT_DIR = Path(
    "data/raw/development"
)


# ============================================================
# VALIDATION TARGETS
# ============================================================

VALIDATION_POINTS = [
    ("UPPER_LEFT",  -5.0, +4.0),
    ("UPPER_RIGHT", +5.0, +4.0),
    ("LOWER_LEFT",  -5.0, -4.0),
    ("LOWER_RIGHT", +5.0, -4.0),
]


# ============================================================
# MEDIAPIPE LANDMARKS
# ============================================================

LEFT_IRIS_CENTER = 473
RIGHT_IRIS_CENTER = 468

RIGHT_EYE_OUTER = 33
RIGHT_EYE_INNER = 133

LEFT_EYE_INNER = 362
LEFT_EYE_OUTER = 263

LEFT_EYE_UPPER = 386
LEFT_EYE_LOWER = 374

RIGHT_EYE_UPPER = 159
RIGHT_EYE_LOWER = 145

# ============================================================
# EYE GEOMETRY
# ============================================================

def normalized_horizontal_position(
    iris_x,
    corner_a_x,
    corner_b_x,
):
    """
    Calculate normalized horizontal iris position
    relative to the horizontal eye corners.

    No clipping or calibration mapping is applied.
    """

    x_min = min(
        corner_a_x,
        corner_b_x,
    )

    x_max = max(
        corner_a_x,
        corner_b_x,
    )

    eye_width = (
        x_max
        - x_min
    )

    if eye_width <= 0:
        return None, None

    ratio = (
        iris_x
        - x_min
    ) / eye_width

    return ratio, eye_width


def normalized_vertical_position(
    iris_y,
    upper_y,
    lower_y,
):
    """
    Calculate normalized vertical iris position
    relative to the upper and lower eyelid landmarks.

    No clipping, rejection, or calibration mapping
    is applied.
    """

    y_min = min(
        upper_y,
        lower_y,
    )

    y_max = max(
        upper_y,
        lower_y,
    )

    eye_aperture = (
        y_max
        - y_min
    )

    if eye_aperture <= 0:
        return None, None

    ratio = (
        iris_y
        - y_min
    ) / eye_aperture

    return ratio, eye_aperture

# ============================================================
# SHARED ACQUISITION STATE
# ============================================================

experiment_clock = core.Clock()

running = False

gaze_samples = []
stimulus_events = []

data_lock = threading.Lock()


# ============================================================
# GAZE ACQUISITION WORKER
# ============================================================

def gaze_worker():
    """
    Continuously acquire camera frames and extract raw
    per-eye geometry in a background thread.

    The timestamp is recorded immediately after cap.read()
    using the shared PsychoPy experiment clock.

    No calibration mapping, smoothing, clipping, or
    quality-based rejection is applied.
    """

    global running

    cap = cv2.VideoCapture(
        CAMERA_INDEX
    )

    cap.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        CAMERA_WIDTH,
    )

    cap.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        CAMERA_HEIGHT,
    )

    cap.set(
        cv2.CAP_PROP_FPS,
        CAMERA_FPS,
    )

    mp_face_mesh = mp.solutions.face_mesh

    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as face_mesh:

        frame_number = 0

        while running:

            success, frame = cap.read()

            timestamp = (
                experiment_clock.getTime()
            )

            if not success:
                continue

            frame_number += 1

            rgb_frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB,
            )

            results = face_mesh.process(
                rgb_frame
            )

            sample = {
                "timestamp": timestamp,
                "frame_number": frame_number,
                "face_detected": 0,

                "left_horizontal_ratio": None,
                "right_horizontal_ratio": None,

                "left_eye_width": None,
                "right_eye_width": None,

                "left_vertical_ratio": None,
                "right_vertical_ratio": None,

                "left_eye_aperture": None,
                "right_eye_aperture": None,
            }

            if results.multi_face_landmarks:

                landmarks = (
                    results
                    .multi_face_landmarks[0]
                    .landmark
                )

                left_horizontal_ratio, left_eye_width = (
                    normalized_horizontal_position(
                        landmarks[
                            LEFT_IRIS_CENTER
                        ].x,
                        landmarks[
                            LEFT_EYE_INNER
                        ].x,
                        landmarks[
                            LEFT_EYE_OUTER
                        ].x,
                    )
                )

                right_horizontal_ratio, right_eye_width = (
                    normalized_horizontal_position(
                        landmarks[
                            RIGHT_IRIS_CENTER
                        ].x,
                        landmarks[
                            RIGHT_EYE_OUTER
                        ].x,
                        landmarks[
                            RIGHT_EYE_INNER
                        ].x,
                    )
                )

                left_vertical_ratio, left_eye_aperture = (
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

                right_vertical_ratio, right_eye_aperture = (
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

                sample.update({
                    "face_detected": 1,

                    "left_horizontal_ratio":
                        left_horizontal_ratio,

                    "right_horizontal_ratio":
                        right_horizontal_ratio,

                    "left_eye_width":
                        left_eye_width,

                    "right_eye_width":
                        right_eye_width,

                    "left_vertical_ratio":
                        left_vertical_ratio,

                    "right_vertical_ratio":
                        right_vertical_ratio,

                    "left_eye_aperture":
                        left_eye_aperture,

                    "right_eye_aperture":
                        right_eye_aperture,
                })

            with data_lock:
                gaze_samples.append(
                    sample
                )

    cap.release()

# ============================================================
# ACQUISITION READINESS
# ============================================================

def wait_for_gaze_ready(
    min_samples=10,
    timeout=10.0,
):
    """
    Wait until the gaze worker has produced a minimum
    number of samples before stimulus presentation begins.

    This is a startup readiness gate only.

    It does not indicate gaze quality or calibration quality.
    """

    start_time = core.getTime()

    while True:

        with data_lock:
            sample_count = len(
                gaze_samples
            )

        if sample_count >= min_samples:
            return True

        if (
            core.getTime()
            - start_time
            >= timeout
        ):
            return False

        core.wait(0.01)


# ============================================================
# STIMULUS EVENT LOGGER
# ============================================================

def record_stimulus_event(
    event_type,
    point_name,
    target_x_deg,
    target_y_deg,
):
    """
    Record a validation stimulus event using the same
    shared experiment clock as gaze acquisition.

    Intended to be called with PsychoPy callOnFlip().
    """

    timestamp = (
        experiment_clock.getTime()
    )

    event = {
        "timestamp": timestamp,
        "event_type": event_type,
        "task":
            "calibration_validation",
        "point_name": point_name,
        "target_x_deg":
            target_x_deg,
        "target_y_deg":
            target_y_deg,
    }

    with data_lock:
        stimulus_events.append(
            event
        )

# ============================================================
# RAW DATA SAVING
# ============================================================

def save_raw_data():
    """
    Save raw validation gaze samples and stimulus events.

    Raw measurements are written without smoothing,
    clipping, calibration mapping, or quality-based
    rejection.
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp_label = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    gaze_path = OUTPUT_DIR / (
        "calibration_validation_gaze_"
        f"{timestamp_label}.csv"
    )

    event_path = OUTPUT_DIR / (
        "calibration_validation_events_"
        f"{timestamp_label}.csv"
    )

    with data_lock:

        gaze_data = list(
            gaze_samples
        )

        event_data = list(
            stimulus_events
        )

    gaze_fields = [
        "timestamp",
        "frame_number",
        "face_detected",
        "left_horizontal_ratio",
        "right_horizontal_ratio",
        "left_eye_width",
        "right_eye_width",
        "left_vertical_ratio",
        "right_vertical_ratio",
        "left_eye_aperture",
        "right_eye_aperture",
    ]

    with gaze_path.open(
        "w",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=gaze_fields,
        )

        writer.writeheader()

        writer.writerows(
            gaze_data
        )

    event_fields = [
        "timestamp",
        "event_type",
        "task",
        "point_name",
        "target_x_deg",
        "target_y_deg",
    ]

    with event_path.open(
        "w",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=event_fields,
        )

        writer.writeheader()

        writer.writerows(
            event_data
        )

    print(
        f"\nSaved gaze data:\n"
        f"{gaze_path}"
    )

    print(
        f"\nSaved stimulus events:\n"
        f"{event_path}"
    )

    return gaze_path, event_path

# ============================================================
# MAIN
# ============================================================

def main():

    global running

    gaze_samples.clear()
    stimulus_events.clear()

    experiment_clock.reset()

    print(
        "\n=== NeuroMirror Phase 1F.3A "
        "— Calibration Validation Acquisition ==="
    )

    print(
        "\nValidation targets:"
    )

    for (
        point_name,
        target_x_deg,
        target_y_deg,
    ) in VALIDATION_POINTS:

        print(
            f"  {point_name:<12} "
            f"X={target_x_deg:+.1f} deg "
            f"Y={target_y_deg:+.1f} deg"
        )

    # --------------------------------------------------------
    # Start gaze acquisition
    # --------------------------------------------------------

    running = True

    gaze_thread = threading.Thread(
        target=gaze_worker,
        daemon=True,
    )

    gaze_thread.start()

    ready = wait_for_gaze_ready(
        min_samples=10,
        timeout=10.0,
    )

    if not ready:

        print(
            "\nERROR: Gaze acquisition "
            "did not become ready."
        )

        running = False

        gaze_thread.join(
            timeout=3.0
        )

        return

    print(
        "\nGaze acquisition ready."
    )

    # --------------------------------------------------------
    # PsychoPy window
    # --------------------------------------------------------

    monitor = monitors.Monitor(
        MONITOR_NAME
    )

    win = visual.Window(
        size=WINDOW_SIZE,
        monitor=monitor,
        units="deg",
        fullscr=False,
        color="lightgray",
    )

    target = visual.Circle(
        win,
        radius=0.4,
        fillColor="black",
        lineColor="black",
        units="deg",
    )

    try:

        # ----------------------------------------------------
        # Present validation targets
        # ----------------------------------------------------

        for (
            point_name,
            target_x_deg,
            target_y_deg,
        ) in VALIDATION_POINTS:

            target.pos = (
                target_x_deg,
                target_y_deg,
            )

            target.draw()

            win.callOnFlip(
                record_stimulus_event,
                "TARGET_ONSET",
                point_name,
                target_x_deg,
                target_y_deg,
            )

            win.flip()

            print(
                f"Presented {point_name:<12} "
                f"X={target_x_deg:+.1f} "
                f"Y={target_y_deg:+.1f}"
            )

            core.wait(
                TARGET_DURATION
            )

    finally:

        win.close()

        running = False

        gaze_thread.join(
            timeout=3.0
        )

    # --------------------------------------------------------
    # Acquisition summary
    # --------------------------------------------------------

    with data_lock:

        total_samples = len(
            gaze_samples
        )

        detected_samples = sum(
            sample["face_detected"]
            for sample in gaze_samples
        )

        event_count = len(
            stimulus_events
        )

    detection_rate = (
        (
            detected_samples
            / total_samples
            * 100.0
        )
        if total_samples
        else 0.0
    )

    print(
        "\nAcquisition summary:"
    )

    print(
        f"Total gaze samples: "
        f"{total_samples}"
    )

    print(
        f"Face detected: "
        f"{detected_samples}"
    )

    print(
        f"Face detection rate: "
        f"{detection_rate:.1f}%"
    )

    print(
        f"Stimulus events: "
        f"{event_count}"
    )

    save_raw_data()


if __name__ == "__main__":
    main()