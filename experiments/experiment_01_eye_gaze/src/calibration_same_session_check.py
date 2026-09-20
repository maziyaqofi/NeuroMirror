"""
NeuroMirror Phase 1F.4
Same-Session Calibration–Validation Check

Purpose
-------
Run the 9-point calibration and 4-point independent validation
sequentially within the same acquisition session.

The purpose is to reduce between-run geometry variation and evaluate
the frozen linear calibration mapping under a same-session condition.

Validation observations must never be used to fit or tune the
calibration model.
"""

from pathlib import Path
import csv
import threading
import time

import cv2
import mediapipe as mp
import numpy as np

from psychopy import core, monitors, visual


# ============================================================
# CONFIGURATION
# ============================================================

MONITOR_NAME = "neuromirror_macbook"

WINDOW_SIZE = (
    1440,
    900,
)

CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_FPS = 30

CALIBRATION_TARGET_DURATION = 2.0
VALIDATION_TARGET_DURATION = 2.0

STABLE_WINDOW_START = 0.300

OUTPUT_DIR = Path(
    "data/raw/development"
)


# ============================================================
# TARGET POSITIONS
# ============================================================

CALIBRATION_POINTS = [
    ("TOP_LEFT", -10.0, +8.0),
    ("TOP_CENTER", 0.0, +8.0),
    ("TOP_RIGHT", +10.0, +8.0),

    ("MIDDLE_LEFT", -10.0, 0.0),
    ("CENTER", 0.0, 0.0),
    ("MIDDLE_RIGHT", +10.0, 0.0),

    ("BOTTOM_LEFT", -10.0, -8.0),
    ("BOTTOM_CENTER", 0.0, -8.0),
    ("BOTTOM_RIGHT", +10.0, -8.0),
]

VALIDATION_POINTS = [
    ("UPPER_LEFT", -5.0, +4.0),
    ("UPPER_RIGHT", +5.0, +4.0),
    ("LOWER_LEFT", -5.0, -4.0),
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
# FEATURE ORDER
# ============================================================

FEATURE_NAMES = [
    "left_horizontal_ratio",
    "right_horizontal_ratio",
    "left_vertical_ratio",
    "right_vertical_ratio",
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
    relative to the two eye-corner landmarks.

    No clipping is applied.
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
        (iris_x - x_min)
        / eye_width
    )

    return ratio, eye_width


def normalized_vertical_position(
    iris_y,
    upper_y,
    lower_y,
):
    """
    Calculate normalized vertical iris position
    relative to the upper and lower eyelid landmarks.

    No clipping is applied.
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
        (iris_y - y_min)
        / eye_aperture
    )

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
    eye-geometry features in a background thread.

    Calibration and validation share this same worker
    and the same experiment clock.
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

    mp_face_mesh = (
        mp.solutions.face_mesh
    )

    frame_number = 0

    with mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as face_mesh:

        while running:

            success, frame = cap.read()

            # Timestamp immediately after frame acquisition,
            # before MediaPipe processing.
            timestamp = experiment_clock.getTime()

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
    Wait until the background gaze worker has produced
    a minimum number of samples before stimulus presentation.

    This is a startup readiness check only.
    It is not a gaze-quality criterion.
    """

    start_time = core.getTime()

    while True:

        with data_lock:
            sample_count = len(
                gaze_samples
            )

        if sample_count >= min_samples:

            print(
                f"Gaze acquisition ready: "
                f"{sample_count} samples"
            )

            return True

        if (
            core.getTime()
            - start_time
            >= timeout
        ):

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
    phase,
    point_name,
    target_x_deg,
    target_y_deg,
):
    """
    Record a stimulus onset using the shared experiment clock.

    Intended to be called through PsychoPy win.callOnFlip()
    so the timestamp corresponds to the software-recorded
    display flip.
    """

    event = {
        "timestamp":
            experiment_clock.getTime(),

        "event_type":
            "target_onset",

        "phase":
            phase,

        "point_name":
            point_name,

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
# TARGET PRESENTATION
# ============================================================

def present_target_sequence(
    win,
    target_stimulus,
    points,
    phase,
    target_duration,
):
    """
    Present a sequence of gaze targets.

    Calibration and validation use the same presentation
    mechanism. Only the target positions, phase label,
    and duration are supplied by the caller.

    Stimulus onset is recorded through win.callOnFlip()
    using the shared experiment clock.
    """

    for (
        point_name,
        target_x,
        target_y,
    ) in points:

        target_stimulus.pos = (
            target_x,
            target_y,
        )

        target_stimulus.draw()

        win.callOnFlip(
            record_stimulus_event,
            phase,
            point_name,
            target_x,
            target_y,
        )

        win.flip()

        print(
            f"{phase.upper():<11} "
            f"{point_name:<14} "
            f"X={target_x:+5.1f} "
            f"Y={target_y:+5.1f}"
        )

        core.wait(
            target_duration
        )

# ============================================================
# RAW DATA SAVING
# ============================================================

def save_raw_data(
    session_timestamp,
):
    """
    Save the complete gaze stream and stimulus-event timeline
    from the same-session calibration-validation run.

    Raw data are written without filtering, smoothing,
    clipping, or calibration mapping.
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    gaze_path = OUTPUT_DIR / (
        f"same_session_gaze_"
        f"{session_timestamp}.csv"
    )

    event_path = OUTPUT_DIR / (
        f"same_session_events_"
        f"{session_timestamp}.csv"
    )

    with data_lock:

        gaze_data = list(
            gaze_samples
        )

        event_data = list(
            stimulus_events
        )

    gaze_fieldnames = [
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
            fieldnames=gaze_fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            gaze_data
        )

    event_fieldnames = [
        "timestamp",
        "event_type",
        "phase",
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
            fieldnames=event_fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            event_data
        )

    print(
        "\nRaw data saved:"
    )

    print(
        gaze_path
    )

    print(
        event_path
    )

    return (
        gaze_path,
        event_path,
    )

# ============================================================
# MAIN
# ============================================================

def main():

    global running

    print(
        "\n=== NeuroMirror Phase 1F.4 — "
        "Same-Session Calibration–Validation Check ==="
    )

    # --------------------------------------------------------
    # Reset session state
    # --------------------------------------------------------

    with data_lock:
        gaze_samples.clear()
        stimulus_events.clear()

    experiment_clock.reset()

    session_timestamp = time.strftime(
        "%Y%m%d_%H%M%S"
    )

    # --------------------------------------------------------
    # Start gaze acquisition
    # --------------------------------------------------------

    running = True

    worker = threading.Thread(
        target=gaze_worker,
        daemon=True,
    )

    worker.start()

    try:

        ready = wait_for_gaze_ready(
            min_samples=10,
            timeout=10.0,
        )

        if not ready:
            raise RuntimeError(
                "Gaze acquisition did not become ready."
            )

        # ----------------------------------------------------
        # PsychoPy window
        # ----------------------------------------------------

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

        target_stimulus = visual.Circle(
            win=win,
            radius=0.4,
            fillColor="black",
            lineColor="black",
            units="deg",
        )

        try:

            # ------------------------------------------------
            # 9-point calibration
            # ------------------------------------------------

            print(
                "\nStarting 9-point calibration..."
            )

            present_target_sequence(
                win,
                target_stimulus,
                CALIBRATION_POINTS,
                "calibration",
                CALIBRATION_TARGET_DURATION,
            )

            # ------------------------------------------------
            # Immediate validation
            # ------------------------------------------------

            print(
                "\nStarting 4-point validation..."
            )

            present_target_sequence(
                win,
                target_stimulus,
                VALIDATION_POINTS,
                "validation",
                VALIDATION_TARGET_DURATION,
            )

        finally:

            win.close()

    finally:

        # ----------------------------------------------------
        # Stop acquisition safely
        # ----------------------------------------------------

        running = False

        worker.join(
            timeout=5.0
        )

    # --------------------------------------------------------
    # Session summary
    # --------------------------------------------------------

    with data_lock:

        total_gaze = len(
            gaze_samples
        )

        face_detected = sum(
            sample["face_detected"]
            for sample in gaze_samples
        )

        total_events = len(
            stimulus_events
        )

    if total_gaze > 0:

        face_rate = (
            face_detected
            / total_gaze
            * 100.0
        )

    else:

        face_rate = 0.0

    print(
        "\nSession summary:"
    )

    print(
        f"Gaze samples: {total_gaze}"
    )

    print(
        f"Face detected: "
        f"{face_detected}/{total_gaze} "
        f"({face_rate:.1f}%)"
    )

    print(
        f"Stimulus events: "
        f"{total_events}"
    )

    # --------------------------------------------------------
    # Save raw session
    # --------------------------------------------------------

    save_raw_data(
        session_timestamp
    )


if __name__ == "__main__":
    main()