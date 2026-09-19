from pathlib import Path
from datetime import datetime
import csv
import threading

import cv2
import mediapipe as mp

from psychopy import visual, monitors, core, event

from randomization import (
    generate_balanced_sequence,
    generate_random_iti_sequence,
)


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
MIN_ITI = 1.0
MAX_ITI = 1.5

TARGET_ECCENTRICITY = 10.0

TEST_SEED = 20260918

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


# ============================================================
# HELPERS
# ============================================================

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


def escape_pressed():
    return (
        "escape"
        in event.getKeys()
    )


def record_stimulus_event(
    event_type,
    trial,
    direction=None,
    eccentricity=None,
    planned_iti_s=None
):
    timestamp = (
        experiment_clock.getTime()
    )

    with data_lock:

        stimulus_events.append({
            "timestamp": timestamp,
            "event_type": event_type,
            "task": "prosaccade",
            "trial": trial,
            "target_direction": direction,
            "target_eccentricity_deg": eccentricity,
            "planned_iti_s": planned_iti_s,
        })


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

            # Software acquisition timestamp:
            # immediately after cap.read()
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

                left_iris_x = (
                    landmarks[
                        LEFT_IRIS_CENTER
                    ].x
                )

                right_iris_x = (
                    landmarks[
                        RIGHT_IRIS_CENTER
                    ].x
                )

                left_ratio = (
                    normalized_horizontal_position(
                        left_iris_x,
                        landmarks[
                            LEFT_EYE_INNER
                        ].x,
                        landmarks[
                            LEFT_EYE_OUTER
                        ].x,
                    )
                )

                right_ratio = (
                    normalized_horizontal_position(
                        right_iris_x,
                        landmarks[
                            RIGHT_EYE_OUTER
                        ].x,
                        landmarks[
                            RIGHT_EYE_INNER
                        ].x,
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

# ============================================================
# STIMULUS HELPERS
# ============================================================

def hold_stimulus(
    win,
    stimulus,
    duration
):
    timer = core.Clock()

    while (
        timer.getTime()
        < duration
    ):

        if escape_pressed():
            return True

        stimulus.draw()
        win.flip()

    return False


def hold_blank(
    win,
    duration
):
    timer = core.Clock()

    while (
        timer.getTime()
        < duration
    ):

        if escape_pressed():
            return True

        win.flip()

    return False


# ============================================================
# TRIAL
# ============================================================

def run_trial(
    win,
    fixation,
    left_target,
    right_target,
    trial_number,
    direction,
    iti_duration
):

    # --------------------------------------------------------
    # CENTRAL FIXATION
    # --------------------------------------------------------

    fixation.draw()

    win.callOnFlip(
        record_stimulus_event,
        "fixation_onset",
        trial_number,
        direction,
        (
            TARGET_ECCENTRICITY
            if direction == "right"
            else -TARGET_ECCENTRICITY
        ),
        iti_duration
    )

    win.flip()

    aborted = hold_stimulus(
        win,
        fixation,
        FIXATION_DURATION
    )

    if aborted:
        return True

    # --------------------------------------------------------
    # TARGET
    # --------------------------------------------------------

    if direction == "right":

        target = right_target
        eccentricity = (
            TARGET_ECCENTRICITY
        )

    else:

        target = left_target
        eccentricity = (
            -TARGET_ECCENTRICITY
        )

    target.draw()

    win.callOnFlip(
        record_stimulus_event,
        "target_onset",
        trial_number,
        direction,
        eccentricity,
        iti_duration
    )

    win.flip()

    aborted = hold_stimulus(
        win,
        target,
        TARGET_DURATION
    )

    if aborted:
        return True

    # --------------------------------------------------------
    # TARGET OFFSET + ITI
    # --------------------------------------------------------

    win.callOnFlip(
        record_stimulus_event,
        "target_offset",
        trial_number,
        direction,
        eccentricity,
        iti_duration
    )

    win.callOnFlip(
        record_stimulus_event,
        "iti_onset",
        trial_number,
        direction,
        eccentricity,
        iti_duration
    )

    win.flip()

    aborted = hold_blank(
        win,
        iti_duration
    )

    if aborted:
        return True

    win.callOnFlip(
        record_stimulus_event,
        "iti_offset",
        trial_number,
        direction,
        eccentricity,
        iti_duration
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
            "prosaccade_20trial_gaze_"
            f"{timestamp_string}.csv"
        )
    )

    event_path = (
        OUTPUT_DIR
        / (
            "prosaccade_20trial_events_"
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
        "trial",
        "target_direction",
        "target_eccentricity_deg",
        "planned_iti_s",
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


# ============================================================
# MAIN
# ============================================================

def main():

    global running

    print(
        "\n=== NeuroMirror Phase 1E "
        "— 20-Trial Randomized Prosaccade + Gaze ===\n"
    )

    sequence, attempts = (
        generate_balanced_sequence(
            trials_per_direction=10,
            max_consecutive=3,
            seed=TEST_SEED
        )
    )

    iti_sequence = generate_random_iti_sequence(
        num_trials=20,
        min_duration=MIN_ITI,
        max_duration=MAX_ITI,
        seed=TEST_SEED,
    )

    print(
        f"Random seed        : "
        f"{TEST_SEED}"
    )

    print(
        f"Generation attempts: "
        f"{attempts}"
    )

    print("\nTrial sequence:")

    for trial_number, (direction, iti_duration) in enumerate(
        zip(sequence, iti_sequence),
        start=1
    ):
        print(
            f"\nStarting trial "
            f"{trial_number} "
            f"({direction.upper()}) | "
            f"ITI={iti_duration:.4f}s"
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

    right_target = visual.Circle(
        win,
        radius=0.4,
        pos=(
            TARGET_ECCENTRICITY,
            0
        ),
        fillColor="black",
        lineColor="black"
    )

    left_target = visual.Circle(
        win,
        radius=0.4,
        pos=(
            -TARGET_ECCENTRICITY,
            0
        ),
        fillColor="black",
        lineColor="black"
    )

    # Allow PsychoPy window to settle
    for _ in range(30):
        win.flip()

    # Start gaze acquisition
    running = True

    worker = threading.Thread(
        target=gaze_worker,
        daemon=True
    )

    worker.start()

    # Wait until the gaze acquisition pipeline is producing data.
    # This replaces the previous fixed 1-second warm-up.
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

    with data_lock:
        ready_sample_count = len(
            gaze_samples
        )

    print(
        f"\nGaze acquisition ready "
        f"({ready_sample_count} samples collected)."
    )

    aborted = False

    for trial_number, (direction, iti_duration) in enumerate(
        zip(sequence, iti_sequence),
        start=1
    ):

        print(
            f"\nStarting trial "
            f"{trial_number} "
            f"({direction.upper()})..."
        )

        aborted = run_trial(
            win=win,
            fixation=fixation,
            left_target=left_target,
            right_target=right_target,
            trial_number=trial_number,
            direction=direction,
            iti_duration=iti_duration
        )

        if aborted:
            break

    running = False

    worker.join(
        timeout=2.0
    )

    win.close()

    gaze_path, event_path = (
        save_data()
    )

    total_samples = len(
        gaze_samples
    )

    detected_samples = sum(
        sample["face_detected"]
        for sample in gaze_samples
    )

    detection_rate = (
        (
            detected_samples
            / total_samples
        ) * 100
        if total_samples
        else 0.0
    )

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
        f"{total_samples}"
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