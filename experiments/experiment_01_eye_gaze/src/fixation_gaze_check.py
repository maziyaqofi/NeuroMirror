from pathlib import Path
from datetime import datetime
import csv
import threading

import cv2
import mediapipe as mp

from psychopy import visual, monitors, core, event


MONITOR_NAME = "neuromirror_macbook"

CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_FPS = 30

FIXATION_DURATION = 10.0
REST_DURATION = 3.0
TOTAL_BLOCKS = 3

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

RIGHT_EYE_OUTER = 33
RIGHT_EYE_INNER = 133

LEFT_EYE_INNER = 362
LEFT_EYE_OUTER = 263


# ============================================================
# SHARED STATE
# ============================================================

experiment_clock = core.Clock()

running = True

gaze_samples = []
stimulus_events = []

data_lock = threading.Lock()

def normalized_horizontal_position(
    iris_x,
    corner_a_x,
    corner_b_x
):
    x_min = min(
        corner_a_x,
        corner_b_x
    )

    x_max = max(
        corner_a_x,
        corner_b_x
    )

    width = x_max - x_min

    if width <= 0:
        return None

    return (
        (iris_x - x_min)
        / width
    )


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

    mp_face_mesh = mp.solutions.face_mesh

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

            # Software acquisition timestamp:
            # immediately after cap.read()
            timestamp = experiment_clock.getTime()

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

                left_iris_x = landmarks[
                    LEFT_IRIS_CENTER
                ].x

                right_iris_x = landmarks[
                    RIGHT_IRIS_CENTER
                ].x

                left_ratio = normalized_horizontal_position(
                    left_iris_x,
                    landmarks[LEFT_EYE_INNER].x,
                    landmarks[LEFT_EYE_OUTER].x,
                )

                right_ratio = normalized_horizontal_position(
                    right_iris_x,
                    landmarks[RIGHT_EYE_OUTER].x,
                    landmarks[RIGHT_EYE_INNER].x,
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
                    "left_iris_ratio": left_ratio,
                    "right_iris_ratio": right_ratio,
                    "average_iris_ratio": average_ratio,
                })

    cap.release()

def wait_for_gaze_ready(
    min_samples=10,
    timeout=10.0
):
    """
    Wait until the gaze acquisition pipeline has produced
    a minimum number of samples.

    This is a startup readiness check only.
    It is not a gaze-quality criterion.
    """

    start_time = core.getTime()

    while True:

        with data_lock:
            sample_count = len(gaze_samples)

        if sample_count >= min_samples:
            return True

        if (
            core.getTime()
            - start_time
            >= timeout
        ):
            return False

        core.wait(0.01)


def record_stimulus_event(
    event_type,
    block
):
    timestamp = experiment_clock.getTime()

    with data_lock:

        stimulus_events.append({
            "timestamp": timestamp,
            "event_type": event_type,
            "task": "fixation",
            "block": block,
        })

def escape_pressed():
    return "escape" in event.getKeys()


def run_fixation(
    win,
    fixation,
    block_number
):
    # --------------------------------------------------------
    # FIXATION ONSET
    # --------------------------------------------------------

    fixation.draw()

    win.callOnFlip(
        record_stimulus_event,
        "fixation_onset",
        block_number
    )

    win.flip()

    timer = core.Clock()

    # --------------------------------------------------------
    # FIXATION PERIOD
    # --------------------------------------------------------

    while timer.getTime() < FIXATION_DURATION:

        if escape_pressed():
            return None, True

        fixation.draw()
        win.flip()

    duration = timer.getTime()

    # --------------------------------------------------------
    # FIXATION OFFSET
    # --------------------------------------------------------

    win.callOnFlip(
        record_stimulus_event,
        "fixation_offset",
        block_number
    )

    win.flip()

    return {
        "block": block_number,
        "duration": duration
    }, False


def run_rest(
    win,
    rest_text,
    block_number
):
    # --------------------------------------------------------
    # REST ONSET
    # --------------------------------------------------------

    rest_text.draw()

    win.callOnFlip(
        record_stimulus_event,
        "rest_onset",
        block_number
    )

    win.flip()

    timer = core.Clock()

    # --------------------------------------------------------
    # REST PERIOD
    # --------------------------------------------------------

    while timer.getTime() < REST_DURATION:

        if escape_pressed():
            return True

        rest_text.draw()
        win.flip()

    # --------------------------------------------------------
    # REST OFFSET
    # --------------------------------------------------------

    win.callOnFlip(
        record_stimulus_event,
        "rest_offset",
        block_number
    )

    win.flip()

    return False

# ============================================================
# SAVE DATA
# ============================================================

def save_data():

    timestamp_string = (
        datetime.now()
        .strftime("%Y%m%d_%H%M%S")
    )

    gaze_path = (
        OUTPUT_DIR
        / (
            "fixation_gaze_"
            f"{timestamp_string}.csv"
        )
    )

    event_path = (
        OUTPUT_DIR
        / (
            "fixation_events_"
            f"{timestamp_string}.csv"
        )
    )

    gaze_fields = [
        "timestamp",
        "frame_number",
        "face_detected",
        "left_iris_ratio",
        "right_iris_ratio",
        "average_iris_ratio",
    ]

    event_fields = [
        "timestamp",
        "event_type",
        "task",
        "block",
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
            gaze_samples
        )

    with event_path.open(
        "w",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=event_fields
        )

        writer.writeheader()
        writer.writerows(
            stimulus_events
        )

    return gaze_path, event_path

def main():

    global running

    print(
        "\n=== NeuroMirror Phase 1G.2 — Fixation + Gaze Integration ==="
    )

    monitor = monitors.Monitor(
        MONITOR_NAME
    )

    win = visual.Window(
        size=(1200, 750),
        fullscr=False,
        monitor=monitor,
        units="deg",
        color="lightgray"
    )

    fixation = visual.TextStim(
        win,
        text="+",
        pos=(0, 0),
        height=1.0,
        color="black"
    )

    rest_text = visual.TextStim(
        win,
        text="Rest",
        pos=(0, 0),
        height=0.7,
        color="black"
    )

    instruction = visual.TextStim(
        win,
        text=(
            "FIXATION TASK\n\n"
            "Keep looking at the center (+).\n"
            "Try to keep your eyes as steady as possible.\n\n"
            f"There will be {TOTAL_BLOCKS} fixation blocks,\n"
            f"each lasting {FIXATION_DURATION:.0f} seconds.\n\n"
            "Press SPACE when you are ready."
        ),
        pos=(0, 0),
        height=0.65,
        color="black",
        wrapWidth=26,
        alignText="center",
    )

    # Allow PsychoPy window to settle
    for _ in range(30):
        win.flip()

    # --------------------------------------------------------
    # INSTRUCTION
    # --------------------------------------------------------

    instruction.draw()
    win.flip()

    keys = event.waitKeys(
        keyList=["space", "escape"]
    )

    if "escape" in keys:
        win.close()
        return

    # --------------------------------------------------------
    # START GAZE ACQUISITION
    # --------------------------------------------------------

    running = True

    worker = threading.Thread(
        target=gaze_worker,
        daemon=True
    )

    worker.start()

    gaze_ready = wait_for_gaze_ready(
        min_samples=10,
        timeout=10.0
    )

    if not gaze_ready:

        print(
            "\nERROR: Gaze acquisition did not become "
            "ready within 10 seconds."
        )

        running = False

        worker.join(
            timeout=2.0
        )

        win.close()
        return

    print("\nGaze acquisition ready.")

    print(
        f"Total fixation blocks : {TOTAL_BLOCKS}"
    )

    print(
        f"Fixation duration     : "
        f"{FIXATION_DURATION:.1f} s"
    )

    print(
        f"Rest duration         : "
        f"{REST_DURATION:.1f} s"
    )

    results = []
    aborted = False

    # --------------------------------------------------------
    # FIXATION BLOCKS
    # --------------------------------------------------------

    for block in range(
        1,
        TOTAL_BLOCKS + 1
    ):

        print(
            f"\nStarting fixation block "
            f"{block}..."
        )

        result, aborted = run_fixation(
            win=win,
            fixation=fixation,
            block_number=block
        )

        if aborted:
            break

        results.append(
            result
        )

        print(
            f"Block {block} completed "
            f"({result['duration']:.4f} s)"
        )

        if block < TOTAL_BLOCKS:

            print("Rest...")

            aborted = run_rest(
                win=win,
                rest_text=rest_text,
                block_number=block
            )

            if aborted:
                break

    # --------------------------------------------------------
    # STOP GAZE ACQUISITION
    # --------------------------------------------------------

    running = False

    worker.join(
        timeout=2.0
    )

    win.close()
    gaze_path, event_path = save_data()

    print(
        "\n"
        + "=" * 55
    )

    if aborted:
        print(
            "Status              : "
            "ABORTED BY USER"
        )
    else:
        print(
            "Status              : "
            "COMPLETED"
        )

    print(
        f"Gaze samples        : "
        f"{len(gaze_samples)}"
    )

    detected_samples = sum(
        sample["face_detected"]
        for sample in gaze_samples
    )

    detection_rate = (
        (
            detected_samples
            / len(gaze_samples)
        ) * 100
        if gaze_samples
        else 0.0
    )

    print(
        f"Face detected       : "
        f"{detected_samples}"
    )

    print(
        f"Face detection rate : "
        f"{detection_rate:.2f}%"
    )

    print(
        f"Stimulus events     : "
        f"{len(stimulus_events)}"
    )

    print(
        f"\nGaze file  : "
        f"{gaze_path}"
    )

    print(
        f"Event file : "
        f"{event_path}"
    )

    print(
        "=" * 55
    )


if __name__ == "__main__":
    main()