from pathlib import Path
from datetime import datetime
import csv
import threading

import cv2
import mediapipe as mp

from psychopy import visual, monitors, core, event


# ============================================================
# CONFIGURATION
# ============================================================

MONITOR_NAME = "neuromirror_macbook"

CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_FPS = 30

TARGET_ECCENTRICITY = 8.0
CONDITION_DURATION = 5.0

CONDITIONS = [
    ("CENTER_1", 0.0),
    ("TOP", TARGET_ECCENTRICITY),
    ("CENTER_2", 0.0),
    ("BOTTOM", -TARGET_ECCENTRICITY),
    ("CENTER_3", 0.0),
]


# ============================================================
# OUTPUT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "development"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# MEDIAPIPE LANDMARK CONFIGURATION
# ============================================================

LEFT_IRIS_CENTER = 473
RIGHT_IRIS_CENTER = 468

LEFT_EYE_UPPER = 386
LEFT_EYE_LOWER = 374

RIGHT_EYE_UPPER = 159
RIGHT_EYE_LOWER = 145


# ============================================================
# SHARED STATE
# ============================================================

experiment_clock = core.Clock()

running = True

gaze_samples = []
stimulus_events = []

data_lock = threading.Lock()


# ============================================================
# VERTICAL GEOMETRY
# ============================================================

def normalized_vertical_position(
    iris_y,
    upper_y,
    lower_y
):
    """
    Calculate normalized vertical iris position
    relative to the selected upper and lower
    eyelid landmarks.

    This is an experimental eye-geometry signal,
    not a calibrated screen-gaze estimate.
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
# BASIC HELPERS
# ============================================================

def escape_pressed():
    return (
        "escape"
        in event.getKeys()
    )

# ============================================================
# GAZE WORKER
# ============================================================

def gaze_worker():

    global running

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

            if not success:
                continue

            # Shared software acquisition timestamp:
            # immediately after cap.read().
            timestamp = (
                experiment_clock.getTime()
            )

            frame_number += 1

            rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            results = face_mesh.process(
                rgb
            )

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

            with data_lock:

                gaze_samples.append({
                    "timestamp": timestamp,
                    "frame_number": frame_number,
                    "face_detected": face_detected,
                    "left_vertical_ratio": left_ratio,
                    "right_vertical_ratio": right_ratio,
                    "average_vertical_ratio": average_ratio,
                })

    cap.release()

# ============================================================
# ACQUISITION READINESS
# ============================================================

def wait_for_gaze_ready(
    min_samples=10,
    timeout=10.0
):
    """
    Wait until the background gaze worker has
    produced enough samples before starting
    the visual stimulus sequence.

    This is a startup readiness criterion only,
    not a gaze-quality threshold.
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
                f"\nGaze acquisition ready "
                f"({sample_count} samples collected)."
            )

            return True

        elapsed = (
            experiment_clock.getTime()
            - start_time
        )

        if elapsed >= timeout:

            print(
                "\nGaze acquisition readiness "
                "timeout."
            )

            return False

        core.wait(0.01)

# ============================================================
# STIMULUS EVENT LOGGING
# ============================================================

def record_stimulus_event(
    event_type,
    condition,
    position_y
):
    """
    Record a visual stimulus event using the
    same software clock as gaze acquisition.
    """

    timestamp = (
        experiment_clock.getTime()
    )

    with data_lock:

        stimulus_events.append({
            "timestamp": timestamp,
            "event_type": event_type,
            "task": "vertical_direction_check",
            "condition": condition,
            "target_x_deg": 0.0,
            "target_y_deg": position_y,
        })

# ============================================================
# RAW DATA SAVING
# ============================================================

def save_raw_data():
    """
    Save synchronized gaze samples and stimulus events
    as separate raw CSV files.

    Raw data are preserved without filtering,
    smoothing, calibration, or interpretation.
    """

    run_timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    gaze_path = (
        OUTPUT_DIR
        / f"vertical_visual_gaze_{run_timestamp}.csv"
    )

    events_path = (
        OUTPUT_DIR
        / f"vertical_visual_events_{run_timestamp}.csv"
    )

    with data_lock:

        gaze_snapshot = list(
            gaze_samples
        )

        event_snapshot = list(
            stimulus_events
        )

    # --------------------------------------------------------
    # GAZE DATA
    # --------------------------------------------------------

    gaze_fields = [
        "timestamp",
        "frame_number",
        "face_detected",
        "left_vertical_ratio",
        "right_vertical_ratio",
        "average_vertical_ratio",
    ]

    with gaze_path.open(
        "w",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=gaze_fields
        )

        writer.writeheader()

        writer.writerows(
            gaze_snapshot
        )

    # --------------------------------------------------------
    # STIMULUS EVENTS
    # --------------------------------------------------------

    event_fields = [
        "timestamp",
        "event_type",
        "task",
        "condition",
        "target_x_deg",
        "target_y_deg",
    ]

    with events_path.open(
        "w",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=event_fields
        )

        writer.writeheader()

        writer.writerows(
            event_snapshot
        )

    return (
        gaze_path,
        events_path
    )

def main():

    global running

    print(
        "\n=== NeuroMirror Phase 1F.1D "
        "— Synchronized Vertical Visual + Gaze Check ===\n"
    )

    print(
        f"Target eccentricity : "
        f"±{TARGET_ECCENTRICITY:.1f} deg"
    )

    print(
        f"Condition duration  : "
        f"{CONDITION_DURATION:.1f} s"
    )

    print(
        "\nCondition sequence:"
    )

    for condition, position_y in CONDITIONS:

        print(
            f"  {condition:8s} "
            f"y={position_y:+.1f} deg"
        )

    # --------------------------------------------------------
    # RESET SHARED DATA
    # --------------------------------------------------------

    with data_lock:
        gaze_samples.clear()
        stimulus_events.clear()

    experiment_clock.reset()

    # --------------------------------------------------------
    # START GAZE ACQUISITION
    # --------------------------------------------------------

    running = True

    gaze_thread = threading.Thread(
        target=gaze_worker,
        daemon=True
    )

    gaze_thread.start()

    print(
        "\nStarting gaze acquisition..."
    )

    ready = wait_for_gaze_ready(
        min_samples=10,
        timeout=10.0
    )

    if not ready:

        running = False

        gaze_thread.join(
            timeout=2.0
        )

        print(
            "\nUnable to start diagnostic "
            "because gaze acquisition "
            "was not ready."
        )

        return

    # --------------------------------------------------------
    # PSYCHOPY WINDOW
    # --------------------------------------------------------

    monitor = monitors.Monitor(
        MONITOR_NAME
    )

    print(
        f"\nMonitor width    : "
        f"{monitor.getWidth()} cm"
    )

    print(
        f"Viewing distance : "
        f"{monitor.getDistance()} cm"
    )

    print(
        f"Monitor size     : "
        f"{monitor.getSizePix()}"
    )

    win = visual.Window(
        size=(1440, 900),
        fullscr=False,
        monitor=monitor,
        units="deg",
        color="lightgray"
    )

    target = visual.Circle(
        win,
        radius=0.4,
        pos=(0, 0),
        fillColor="black",
        lineColor="black"
    )

    ready_text = visual.TextStim(
        win,
        text=(
            "Vertical visual + gaze check\n\n"
            "Follow the black dot with your eyes.\n"
            "Keep your head as still as possible.\n\n"
            "Press SPACE to start\n"
            "Press ESC to abort"
        ),
        pos=(0, 0),
        height=0.6,
        color="black",
        alignText="center"
    )

    ready_text.draw()
    win.flip()

    keys = event.waitKeys(
        keyList=[
            "space",
            "escape"
        ]
    )

    if "escape" in keys:

        win.close()

        running = False

        gaze_thread.join(
            timeout=2.0
        )

        print(
            "\nDiagnostic aborted."
        )

        return

    event.clearEvents()

    # --------------------------------------------------------
    # SYNCHRONIZED CONDITION SEQUENCE
    # --------------------------------------------------------

    print(
        "\nStarting synchronized "
        "condition sequence..."
    )

    aborted = False

    for condition, position_y in CONDITIONS:

        target.pos = (
            0,
            position_y
        )

        target.draw()

        win.callOnFlip(
            record_stimulus_event,
            "target_onset",
            condition,
            position_y
        )

        win.flip()

        print(
            f"  {condition:8s} | "
            f"y={position_y:+.1f} deg"
        )

        condition_clock = core.Clock()

        while (
            condition_clock.getTime()
            < CONDITION_DURATION
        ):

            if escape_pressed():

                aborted = True
                break

            core.wait(0.005)

        if aborted:
            break

    # --------------------------------------------------------
    # STOP ACQUISITION
    # --------------------------------------------------------

    win.close()

    running = False

    gaze_thread.join(
        timeout=2.0
    )

    if aborted:

        print(
            "\nDiagnostic aborted during "
            "condition sequence."
        )

        return

    # --------------------------------------------------------
    # BASIC RUN SUMMARY
    # --------------------------------------------------------

    with data_lock:

        sample_count = len(
            gaze_samples
        )

        valid_count = sum(
            1
            for sample in gaze_samples
            if (
                sample[
                    "average_vertical_ratio"
                ]
                is not None
            )
        )

        event_count = len(
            stimulus_events
        )

        event_snapshot = list(
            stimulus_events
        )

    print(
        "\n=== RUN SUMMARY ==="
    )

    print(
        f"Total gaze samples : "
        f"{sample_count}"
    )

    print(
        f"Valid vertical     : "
        f"{valid_count}"
    )

    if sample_count > 0:

        valid_proportion = (
            valid_count
            / sample_count
        ) * 100.0

        print(
            f"Valid proportion   : "
            f"{valid_proportion:.1f}%"
        )

    print(
        f"Stimulus events    : "
        f"{event_count}"
    )

    print(
        "\nStimulus onset timestamps:"
    )

    for stimulus_event in event_snapshot:

        print(
            f"  "
            f"{stimulus_event['condition']:8s} | "
            f"y="
            f"{stimulus_event['target_y_deg']:+.1f} deg | "
            f"t="
            f"{stimulus_event['timestamp']:.4f} s"
        )

    # --------------------------------------------------------
    # SAVE RAW DATA
    # --------------------------------------------------------

    gaze_path, events_path = (
        save_raw_data()
    )

    print(
        "\nRaw data saved:"
    )

    print(
        f"  Gaze   : {gaze_path}"
    )

    print(
        f"  Events : {events_path}"
    )

    print(
        "\nSynchronized vertical visual "
        "+ gaze check finished."
    )

if __name__ == "__main__":
    main()