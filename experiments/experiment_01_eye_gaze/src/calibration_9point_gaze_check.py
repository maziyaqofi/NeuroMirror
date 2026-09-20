from pathlib import Path
from datetime import datetime
import csv
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

HORIZONTAL_ECCENTRICITY = 10.0
VERTICAL_ECCENTRICITY = 8.0

TARGET_DURATION = 2.0

OUTPUT_DIR = Path(
    "data/raw/development"
)


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
# 9-POINT CALIBRATION LAYOUT
# ============================================================

CALIBRATION_POINTS = [
    (
        "TOP_LEFT",
        -HORIZONTAL_ECCENTRICITY,
        +VERTICAL_ECCENTRICITY,
    ),
    (
        "TOP_CENTER",
        0.0,
        +VERTICAL_ECCENTRICITY,
    ),
    (
        "TOP_RIGHT",
        +HORIZONTAL_ECCENTRICITY,
        +VERTICAL_ECCENTRICITY,
    ),

    (
        "MIDDLE_LEFT",
        -HORIZONTAL_ECCENTRICITY,
        0.0,
    ),
    (
        "CENTER",
        0.0,
        0.0,
    ),
    (
        "MIDDLE_RIGHT",
        +HORIZONTAL_ECCENTRICITY,
        0.0,
    ),

    (
        "BOTTOM_LEFT",
        -HORIZONTAL_ECCENTRICITY,
        -VERTICAL_ECCENTRICITY,
    ),
    (
        "BOTTOM_CENTER",
        0.0,
        -VERTICAL_ECCENTRICITY,
    ),
    (
        "BOTTOM_RIGHT",
        +HORIZONTAL_ECCENTRICITY,
        -VERTICAL_ECCENTRICITY,
    ),
]

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
    relative to the two eye corners.

    This is an experimental eye-geometry signal,
    not a calibrated screen-gaze coordinate.
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
        x_max - x_min
    )

    if eye_width <= 0:
        return None, eye_width

    ratio = (
        iris_x - x_min
    ) / eye_width

    return ratio, eye_width



def normalized_vertical_position(
    iris_y,
    upper_y,
    lower_y,
):
    """
    Calculate normalized vertical iris position
    relative to upper and lower eyelid landmarks.

    Eye aperture is returned separately as a
    per-eye geometry quality feature.

    No aperture-based rejection is applied here.
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
        y_max - y_min
    )

    if eye_aperture <= 0:
        return None, eye_aperture

    ratio = (
        iris_y - y_min
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
    Background camera and MediaPipe worker.

    Records raw per-eye horizontal and vertical geometry
    using the shared experiment clock.

    No smoothing, calibration mapping, aperture rejection,
    or gaze-quality filtering is applied here.
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

    frame_number = 0

    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as face_mesh:

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
                "left_eye_width": None,
                "left_vertical_ratio": None,
                "left_eye_aperture": None,

                "right_horizontal_ratio": None,
                "right_eye_width": None,
                "right_vertical_ratio": None,
                "right_eye_aperture": None,
            }

            if results.multi_face_landmarks:

                landmarks = (
                    results
                    .multi_face_landmarks[0]
                    .landmark
                )

                # --------------------------------------------
                # LEFT EYE
                # --------------------------------------------

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

                # --------------------------------------------
                # RIGHT EYE
                # --------------------------------------------

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

                    "left_eye_width":
                        left_eye_width,

                    "left_vertical_ratio":
                        left_vertical_ratio,

                    "left_eye_aperture":
                        left_eye_aperture,

                    "right_horizontal_ratio":
                        right_horizontal_ratio,

                    "right_eye_width":
                        right_eye_width,

                    "right_vertical_ratio":
                        right_vertical_ratio,

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
    Wait until the background gaze worker has collected
    a minimum number of samples before calibration begins.

    This is a startup readiness check only.

    It does not guarantee gaze quality, face detection,
    or valid eye geometry.
    """

    start_time = (
        experiment_clock.getTime()
    )

    while True:

        with data_lock:
            sample_count = len(
                gaze_samples
            )

        if sample_count >= min_samples:

            print(
                f"Gaze acquisition ready: "
                f"{sample_count} samples."
            )

            return True

        elapsed = (
            experiment_clock.getTime()
            - start_time
        )

        if elapsed >= timeout:

            print(
                "Gaze acquisition readiness "
                "timeout."
            )

            return False

        core.wait(
            0.01
        )

# ============================================================
# STIMULUS EVENT RECORDING
# ============================================================

def record_stimulus_event(
    event_type,
    point_name,
    target_x_deg,
    target_y_deg,
):
    """
    Record a stimulus event using the shared experiment clock.

    This function is intended to be scheduled with
    PsychoPy win.callOnFlip() so that the event timestamp
    corresponds to the software-recorded display flip.
    """

    event = {
        "timestamp": experiment_clock.getTime(),
        "event_type": event_type,
        "task": "calibration_9point",
        "point_name": point_name,
        "target_x_deg": target_x_deg,
        "target_y_deg": target_y_deg,
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
    Save raw gaze samples and calibration stimulus events.

    Raw data are written without smoothing, filtering,
    clipping, calibration mapping, or frame rejection.
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp_label = (
        datetime.now()
        .strftime("%Y%m%d_%H%M%S")
    )

    gaze_path = OUTPUT_DIR / (
        f"calibration_9point_gaze_"
        f"{timestamp_label}.csv"
    )

    event_path = OUTPUT_DIR / (
        f"calibration_9point_events_"
        f"{timestamp_label}.csv"
    )

    with data_lock:
        gaze_data = list(
            gaze_samples
        )

        event_data = list(
            stimulus_events
        )

    # --------------------------------------------------------
    # GAZE DATA
    # --------------------------------------------------------

    gaze_fields = [
        "timestamp",
        "frame_number",
        "face_detected",

        "left_horizontal_ratio",
        "left_eye_width",
        "left_vertical_ratio",
        "left_eye_aperture",

        "right_horizontal_ratio",
        "right_eye_width",
        "right_vertical_ratio",
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

    # --------------------------------------------------------
    # STIMULUS EVENT DATA
    # --------------------------------------------------------

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

    print(
        "\n=== NeuroMirror Phase 1F.2B "
        "— 9-Point Calibration Gaze Acquisition ==="
    )

    # --------------------------------------------------------
    # RESET SHARED STATE
    # --------------------------------------------------------

    with data_lock:
        gaze_samples.clear()
        stimulus_events.clear()

    experiment_clock.reset()

    # --------------------------------------------------------
    # START GAZE WORKER
    # --------------------------------------------------------

    running = True

    worker = threading.Thread(
        target=gaze_worker,
        daemon=True,
    )

    worker.start()

    # --------------------------------------------------------
    # WAIT FOR ACQUISITION
    # --------------------------------------------------------

    ready = wait_for_gaze_ready(
        min_samples=10,
        timeout=10.0,
    )

    if not ready:

        running = False

        worker.join(
            timeout=2.0
        )

        print(
            "\nCalibration acquisition aborted "
            "because gaze worker was not ready."
        )

        return

    # --------------------------------------------------------
    # CREATE PSYCHOPY WINDOW
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
        win=win,
        radius=0.4,
        fillColor="black",
        lineColor="black",
        units="deg",
    )

    print(
        f"\nHorizontal eccentricity: "
        f"±{HORIZONTAL_ECCENTRICITY:.1f}°"
    )

    print(
        f"Vertical eccentricity: "
        f"±{VERTICAL_ECCENTRICITY:.1f}°"
    )

    print(
        f"Target duration: "
        f"{TARGET_DURATION:.1f} s"
    )

    print(
        "\nStarting 9-point acquisition..."
    )

    # --------------------------------------------------------
    # PRESENT CALIBRATION TARGETS
    # --------------------------------------------------------

    try:

        for index, (
            point_name,
            x_deg,
            y_deg,
        ) in enumerate(
            CALIBRATION_POINTS,
            start=1,
        ):

            target.pos = (
                x_deg,
                y_deg,
            )

            target.draw()

            win.callOnFlip(
                record_stimulus_event,
                "TARGET_ONSET",
                point_name,
                x_deg,
                y_deg,
            )

            win.flip()

            print(
                f"{index:02d}/09 "
                f"{point_name:<14} "
                f"x={x_deg:+5.1f}° "
                f"y={y_deg:+5.1f}°"
            )

            core.wait(
                TARGET_DURATION
            )

    finally:

        # ----------------------------------------------------
        # SAFE SHUTDOWN
        # ----------------------------------------------------

        win.close()

        running = False

        worker.join(
            timeout=3.0
        )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    with data_lock:

        total_samples = len(
            gaze_samples
        )

        detected_samples = sum(
            sample["face_detected"]
            for sample in gaze_samples
        )

        total_events = len(
            stimulus_events
        )

    if total_samples > 0:

        detection_rate = (
            100.0
            * detected_samples
            / total_samples
        )

    else:

        detection_rate = 0.0

    print(
        f"\nTotal gaze samples: "
        f"{total_samples}"
    )

    print(
        f"Face-detected samples: "
        f"{detected_samples}"
    )

    print(
        f"Face detection rate: "
        f"{detection_rate:.1f}%"
    )

    print(
        f"Stimulus events: "
        f"{total_events}"
    )

    # --------------------------------------------------------
    # SAVE RAW DATA
    # --------------------------------------------------------

    save_raw_data()

    print(
        "\n9-point calibration gaze "
        "acquisition complete."
    )


if __name__ == "__main__":
    main()