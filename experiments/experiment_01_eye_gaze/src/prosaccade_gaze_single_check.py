import csv
import cv2
import threading
from pathlib import Path
from datetime import datetime

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

FIXATION_DURATION = 1.0
TARGET_DURATION = 1.0
ITI_DURATION = 1.0

TARGET_ECCENTRICITY = 10.0
TARGET_DIRECTION = "RIGHT"

RIGHT_IRIS_CENTER = 468
LEFT_IRIS_CENTER = 473

RIGHT_EYE_OUTER = 33
RIGHT_EYE_INNER = 133

LEFT_EYE_INNER = 362
LEFT_EYE_OUTER = 263

PROJECT_ROOT = Path(__file__).resolve().parents[3]


# ============================================================
# SHARED STATE
# ============================================================

experiment_clock = core.Clock()

running = True
gaze_samples = []
stimulus_events = []

lock = threading.Lock()


# ============================================================
# HELPERS
# ============================================================

def escape_pressed():
    return "escape" in event.getKeys()


def normalized_horizontal_position(
    landmarks,
    iris_index,
    corner_a,
    corner_b,
):
    iris_x = landmarks[iris_index].x
    x1 = landmarks[corner_a].x
    x2 = landmarks[corner_b].x

    x_min = min(x1, x2)
    x_max = max(x1, x2)

    width = x_max - x_min

    if width <= 0:
        return None

    return (iris_x - x_min) / width


# ============================================================
# GAZE WORKER
# ============================================================

def gaze_worker():

    global running

    cap = cv2.VideoCapture(CAMERA_INDEX)

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

    if not cap.isOpened():
        print("ERROR: Camera could not be opened.")
        running = False
        return

    face_mesh = mp.solutions.face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    frame_number = 0

    while running:

        ret, frame = cap.read()

        if not ret:
            continue

        # Software acquisition timestamp:
        # immediately after cap.read() returns.
        timestamp = experiment_clock.getTime()

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB,
        )

        results = face_mesh.process(rgb)

        frame_number += 1

        left_ratio = None
        right_ratio = None
        average_ratio = None
        face_detected = False

        if results.multi_face_landmarks:

            face_detected = True

            landmarks = (
                results
                .multi_face_landmarks[0]
                .landmark
            )

            right_ratio = (
                normalized_horizontal_position(
                    landmarks,
                    RIGHT_IRIS_CENTER,
                    RIGHT_EYE_OUTER,
                    RIGHT_EYE_INNER,
                )
            )

            left_ratio = (
                normalized_horizontal_position(
                    landmarks,
                    LEFT_IRIS_CENTER,
                    LEFT_EYE_INNER,
                    LEFT_EYE_OUTER,
                )
            )

            if (
                left_ratio is not None
                and right_ratio is not None
            ):
                average_ratio = (
                    left_ratio + right_ratio
                ) / 2.0

        sample = {
            "timestamp": timestamp,
            "frame_number": frame_number,
            "face_detected": int(face_detected),
            "left_iris_ratio": left_ratio,
            "right_iris_ratio": right_ratio,
            "average_iris_ratio": average_ratio,
        }

        with lock:
            gaze_samples.append(sample)

    face_mesh.close()
    cap.release()


# ============================================================
# STIMULUS EVENT LOGGER
# ============================================================

def record_stimulus_event(
    event_type,
    trial,
    target_direction="",
    target_eccentricity_deg="",
):

    timestamp = experiment_clock.getTime()

    with lock:
        stimulus_events.append(
            {
                "timestamp": timestamp,
                "event_type": event_type,
                "task": "prosaccade",
                "trial": trial,
                "target_direction": target_direction,
                "target_eccentricity_deg":
                    target_eccentricity_deg,
            }
        )


# ============================================================
# DISPLAY
# ============================================================

def main():

    global running

    print(
        "\n=== NeuroMirror 1D.4A "
        "— Single Prosaccade + Gaze ===\n"
    )

    print("Instruction:")
    print(
        "Look at the center fixation, then look at "
        "the peripheral dot as quickly as possible."
    )
    print("Keep your head as still as possible.\n")

    monitor = monitors.Monitor(
        MONITOR_NAME
    )

    win = visual.Window(
        size=(1200, 750),
        fullscr=False,
        monitor=monitor,
        units="deg",
        color="lightgray",
    )

    fixation = visual.TextStim(
        win,
        text="+",
        pos=(0, 0),
        height=1.0,
        color="black",
    )

    target = visual.Circle(
        win,
        radius=0.4,
        pos=(TARGET_ECCENTRICITY, 0),
        fillColor="black",
        lineColor="black",
    )

    # --------------------------------------------------------
    # START BACKGROUND GAZE WORKER
    # --------------------------------------------------------

    thread = threading.Thread(
        target=gaze_worker,
        daemon=True,
    )

    thread.start()

    # Brief camera/MediaPipe warm-up.
    core.wait(1.0)

    if not running:
        win.close()
        return

    aborted = False

    # --------------------------------------------------------
    # FIXATION
    # --------------------------------------------------------

    fixation.draw()

    win.callOnFlip(
        record_stimulus_event,
        "fixation_onset",
        1,
        "center",
        0.0,
    )

    win.flip()

    fixation_clock = core.Clock()

    while (
        fixation_clock.getTime()
        < FIXATION_DURATION
        and running
    ):

        if escape_pressed():
            aborted = True
            break

        fixation.draw()
        win.flip()

    # --------------------------------------------------------
    # TARGET
    # --------------------------------------------------------

    if not aborted and running:

        target.draw()

        win.callOnFlip(
            record_stimulus_event,
            "target_onset",
            1,
            TARGET_DIRECTION.lower(),
            TARGET_ECCENTRICITY,
        )

        win.flip()

        target_clock = core.Clock()

        while (
            target_clock.getTime()
            < TARGET_DURATION
            and running
        ):

            if escape_pressed():
                aborted = True
                break

            target.draw()
            win.flip()

    # --------------------------------------------------------
    # ITI
    # --------------------------------------------------------

    if not aborted and running:

        win.callOnFlip(
            record_stimulus_event,
            "target_offset",
            1,
            TARGET_DIRECTION.lower(),
            TARGET_ECCENTRICITY,
        )

        win.callOnFlip(
            record_stimulus_event,
            "iti_onset",
            1,
        )

        win.flip()

        iti_clock = core.Clock()

        while (
            iti_clock.getTime()
            < ITI_DURATION
            and running
        ):

            if escape_pressed():
                aborted = True
                break

            win.flip()

    if not aborted and running:

        win.callOnFlip(
            record_stimulus_event,
            "iti_offset",
            1,
        )

        win.flip()

    # --------------------------------------------------------
    # CLEANUP
    # --------------------------------------------------------

    running = False

    thread.join(
        timeout=2.0
    )

    win.close()

    # --------------------------------------------------------
    # SAVE DATA
    # --------------------------------------------------------

    output_dir = (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "development"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp_string = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    gaze_path = (
        output_dir
        / f"prosaccade_gaze_{timestamp_string}.csv"
    )

    event_path = (
        output_dir
        / f"prosaccade_events_{timestamp_string}.csv"
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
        "trial",
        "target_direction",
        "target_eccentricity_deg",
    ]

    with gaze_path.open(
        "w",
        newline="",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=gaze_fields,
        )

        writer.writeheader()
        writer.writerows(gaze_samples)

    with event_path.open(
        "w",
        newline="",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=event_fields,
        )

        writer.writeheader()
        writer.writerows(stimulus_events)

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    detected = sum(
        sample["face_detected"]
        for sample in gaze_samples
    )

    total = len(gaze_samples)

    detection_rate = (
        detected / total * 100
        if total > 0
        else 0.0
    )

    print("\n" + "=" * 55)

    if aborted:
        print("Status              : ABORTED")
    else:
        print("Status              : COMPLETED")

    print(f"Gaze samples        : {total}")
    print(f"Face detected       : {detected}")
    print(
        f"Face detection rate : "
        f"{detection_rate:.2f}%"
    )
    print(
        f"Stimulus events     : "
        f"{len(stimulus_events)}"
    )

    print(f"\nGaze file  : {gaze_path}")
    print(f"Event file : {event_path}")

    print("=" * 55)


if __name__ == "__main__":
    main()