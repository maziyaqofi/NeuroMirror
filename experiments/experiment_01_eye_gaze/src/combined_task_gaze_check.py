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
# PHASE 1G.3 — COMBINED TASK + GAZE INTEGRATION
# Shared acquisition infrastructure
# ============================================================


# ============================================================
# CONFIGURATION
# ============================================================

MONITOR_NAME = "neuromirror_macbook"

CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_FPS = 30

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
    task,
    block=None,
    trial=None,
    direction=None,
    expected_response_direction=None,
    eccentricity=None,
    planned_iti_s=None
):
    """
    Record an event from any task using the shared experiment clock.

    The same event logger is used for fixation, prosaccade,
    and antisaccade.
    """

    timestamp = (
        experiment_clock.getTime()
    )

    with data_lock:

        stimulus_events.append({
            "timestamp": timestamp,
            "event_type": event_type,
            "task": task,
            "block": block,
            "trial": trial,
            "target_direction": direction,
            "expected_response_direction":
                expected_response_direction,
            "target_eccentricity_deg":
                eccentricity,
            "planned_iti_s":
                planned_iti_s,
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
# FIXATION TASK
# ============================================================

FIXATION_BLOCK_DURATION = 10.0
FIXATION_REST_DURATION = 3.0
FIXATION_TOTAL_BLOCKS = 3


def run_fixation(
    win,
    fixation_stimulus,
    block_number
):
    """
    Run one central fixation block.

    Fixation onset and offset are recorded using the shared
    experiment clock and shared stimulus event logger.
    """

    fixation_stimulus.draw()

    win.callOnFlip(
        record_stimulus_event,
        "fixation_onset",
        "fixation",
        block=block_number,
    )

    win.flip()

    start_time = (
        experiment_clock.getTime()
    )

    while (
        experiment_clock.getTime()
        - start_time
        < FIXATION_BLOCK_DURATION
    ):

        if escape_pressed():
            return False

        fixation_stimulus.draw()
        win.flip()

    fixation_stimulus.draw()

    win.callOnFlip(
        record_stimulus_event,
        "fixation_offset",
        "fixation",
        block=block_number,
    )

    win.flip()

    return True


def run_fixation_rest(
    win,
    rest_stimulus,
    block_number
):
    """
    Run the rest period following a fixation block.
    """

    rest_stimulus.draw()

    win.callOnFlip(
        record_stimulus_event,
        "rest_onset",
        "fixation",
        block=block_number,
    )

    win.flip()

    start_time = (
        experiment_clock.getTime()
    )

    while (
        experiment_clock.getTime()
        - start_time
        < FIXATION_REST_DURATION
    ):

        if escape_pressed():
            return False

        rest_stimulus.draw()
        win.flip()

    rest_stimulus.draw()

    win.callOnFlip(
        record_stimulus_event,
        "rest_offset",
        "fixation",
        block=block_number,
    )

    win.flip()

    return True

# ============================================================
# PROSACCADE TASK
# ============================================================

PROSACCADE_FIXATION_DURATION = 1.0
PROSACCADE_TARGET_DURATION = 1.0

PROSACCADE_MIN_ITI = 1.0
PROSACCADE_MAX_ITI = 1.5

PROSACCADE_TARGET_ECCENTRICITY = 10.0

PROSACCADE_TOTAL_TRIALS = 20
PROSACCADE_SEED = 20260918


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


def run_prosaccade_trial(
    win,
    fixation,
    left_target,
    right_target,
    trial_number,
    direction,
    iti_duration
):
    """
    Run one prosaccade trial using the shared experiment
    clock and shared event logger.
    """

    # --------------------------------------------------------
    # CENTRAL FIXATION
    # --------------------------------------------------------

    eccentricity = (
        PROSACCADE_TARGET_ECCENTRICITY
        if direction == "right"
        else -PROSACCADE_TARGET_ECCENTRICITY
    )

    fixation.draw()

    win.callOnFlip(
        record_stimulus_event,
        "fixation_onset",
        "prosaccade",
        trial=trial_number,
        direction=direction,
        eccentricity=eccentricity,
        planned_iti_s=iti_duration,
    )

    win.flip()

    aborted = hold_stimulus(
        win,
        fixation,
        PROSACCADE_FIXATION_DURATION
    )

    if aborted:
        return True

    # --------------------------------------------------------
    # TARGET
    # --------------------------------------------------------

    if direction == "right":
        target = right_target
    else:
        target = left_target

    target.draw()

    win.callOnFlip(
        record_stimulus_event,
        "target_onset",
        "prosaccade",
        trial=trial_number,
        direction=direction,
        eccentricity=eccentricity,
        planned_iti_s=iti_duration,
    )

    win.flip()

    aborted = hold_stimulus(
        win,
        target,
        PROSACCADE_TARGET_DURATION
    )

    if aborted:
        return True

    # --------------------------------------------------------
    # TARGET OFFSET + ITI
    # --------------------------------------------------------

    win.callOnFlip(
        record_stimulus_event,
        "target_offset",
        "prosaccade",
        trial=trial_number,
        direction=direction,
        eccentricity=eccentricity,
        planned_iti_s=iti_duration,
    )

    win.callOnFlip(
        record_stimulus_event,
        "iti_onset",
        "prosaccade",
        trial=trial_number,
        direction=direction,
        eccentricity=eccentricity,
        planned_iti_s=iti_duration,
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
        "prosaccade",
        trial=trial_number,
        direction=direction,
        eccentricity=eccentricity,
        planned_iti_s=iti_duration,
    )

    win.flip()

    return False

# ============================================================
# ANTISACCADE TASK
# ============================================================

ANTISACCADE_FIXATION_DURATION = 1.0
ANTISACCADE_TARGET_DURATION = 1.0

ANTISACCADE_MIN_ITI = 1.0
ANTISACCADE_MAX_ITI = 1.5

ANTISACCADE_TARGET_ECCENTRICITY = 10.0

ANTISACCADE_TOTAL_TRIALS = 20
ANTISACCADE_SEED = 20260918


def run_antisaccade_trial(
    win,
    fixation,
    left_target,
    right_target,
    trial_number,
    direction,
    iti_duration
):
    """
    Run one antisaccade trial using the shared experiment
    clock and shared event logger.

    Target direction and expected response direction are
    intentionally stored separately.
    """

    # --------------------------------------------------------
    # ANTISACCADE TRIAL CONFIGURATION
    # --------------------------------------------------------

    if direction == "right":

        target = right_target

        target_direction = "right"

        eccentricity = (
            ANTISACCADE_TARGET_ECCENTRICITY
        )

        expected_response_direction = (
            "left"
        )

    elif direction == "left":

        target = left_target

        target_direction = "left"

        eccentricity = (
            -ANTISACCADE_TARGET_ECCENTRICITY
        )

        expected_response_direction = (
            "right"
        )

    else:

        raise ValueError(
            f"Invalid target direction: {direction}"
        )

    # --------------------------------------------------------
    # CENTRAL FIXATION
    # --------------------------------------------------------

    fixation.draw()

    win.callOnFlip(
        record_stimulus_event,
        "fixation_onset",
        "antisaccade",
        trial=trial_number,
        direction=target_direction,
        expected_response_direction=(
            expected_response_direction
        ),
        eccentricity=eccentricity,
        planned_iti_s=iti_duration,
    )

    win.flip()

    aborted = hold_stimulus(
        win,
        fixation,
        ANTISACCADE_FIXATION_DURATION
    )

    if aborted:
        return True

    # --------------------------------------------------------
    # PERIPHERAL TARGET
    # --------------------------------------------------------

    target.draw()

    win.callOnFlip(
        record_stimulus_event,
        "target_onset",
        "antisaccade",
        trial=trial_number,
        direction=target_direction,
        expected_response_direction=(
            expected_response_direction
        ),
        eccentricity=eccentricity,
        planned_iti_s=iti_duration,
    )

    win.flip()

    aborted = hold_stimulus(
        win,
        target,
        ANTISACCADE_TARGET_DURATION
    )

    if aborted:
        return True

    # --------------------------------------------------------
    # TARGET OFFSET + ITI ONSET
    # --------------------------------------------------------

    win.callOnFlip(
        record_stimulus_event,
        "target_offset",
        "antisaccade",
        trial=trial_number,
        direction=target_direction,
        expected_response_direction=(
            expected_response_direction
        ),
        eccentricity=eccentricity,
        planned_iti_s=iti_duration,
    )

    win.callOnFlip(
        record_stimulus_event,
        "iti_onset",
        "antisaccade",
        trial=trial_number,
        direction=target_direction,
        expected_response_direction=(
            expected_response_direction
        ),
        eccentricity=eccentricity,
        planned_iti_s=iti_duration,
    )

    win.flip()

    aborted = hold_blank(
        win,
        iti_duration
    )

    if aborted:
        return True

    # --------------------------------------------------------
    # ITI OFFSET
    # --------------------------------------------------------

    win.callOnFlip(
        record_stimulus_event,
        "iti_offset",
        "antisaccade",
        trial=trial_number,
        direction=target_direction,
        expected_response_direction=(
            expected_response_direction
        ),
        eccentricity=eccentricity,
        planned_iti_s=iti_duration,
    )

    win.flip()

    return False

# ============================================================
# COMBINED SESSION DATA SAVING
# ============================================================

def save_combined_data():

    timestamp_label = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    gaze_path = (
        OUTPUT_DIR
        / f"combined_smoke_gaze_{timestamp_label}.csv"
    )

    event_path = (
        OUTPUT_DIR
        / f"combined_smoke_events_{timestamp_label}.csv"
    )

    with data_lock:

        gaze_snapshot = list(
            gaze_samples
        )

        event_snapshot = list(
            stimulus_events
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
        "trial",
        "target_direction",
        "expected_response_direction",
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
            gaze_snapshot
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
            event_snapshot
        )

    return (
        gaze_path,
        event_path
    )

# ============================================================
# COMBINED SMOKE TEST
# ============================================================

SMOKE_FIXATION_DURATION = 3.0

SMOKE_PROSACCADE_SEED = 20260920
SMOKE_ANTISACCADE_SEED = 20260921


def main():

    global running

    print(
        "\n=== NeuroMirror Phase 1G.3 "
        "— Combined Task Smoke Test ===\n"
    )

    # --------------------------------------------------------
    # DEVELOPMENT RANDOMIZATION
    # --------------------------------------------------------

    prosaccade_sequence, prosaccade_attempts = (
        generate_balanced_sequence(
            trials_per_direction=2,
            max_consecutive=3,
            seed=SMOKE_PROSACCADE_SEED,
        )
    )

    prosaccade_iti = (
        generate_random_iti_sequence(
            num_trials=4,
            min_duration=PROSACCADE_MIN_ITI,
            max_duration=PROSACCADE_MAX_ITI,
            seed=SMOKE_PROSACCADE_SEED,
        )
    )

    antisaccade_sequence, antisaccade_attempts = (
        generate_balanced_sequence(
            trials_per_direction=2,
            max_consecutive=3,
            seed=SMOKE_ANTISACCADE_SEED,
        )
    )

    antisaccade_iti = (
        generate_random_iti_sequence(
            num_trials=4,
            min_duration=ANTISACCADE_MIN_ITI,
            max_duration=ANTISACCADE_MAX_ITI,
            seed=SMOKE_ANTISACCADE_SEED,
        )
    )

    print(
        f"Prosaccade seed      : "
        f"{SMOKE_PROSACCADE_SEED}"
    )

    print(
        f"Prosaccade attempts  : "
        f"{prosaccade_attempts}"
    )

    print(
        f"Prosaccade sequence  : "
        f"{prosaccade_sequence}"
    )

    print(
        f"\nAntisaccade seed     : "
        f"{SMOKE_ANTISACCADE_SEED}"
    )

    print(
        f"Antisaccade attempts : "
        f"{antisaccade_attempts}"
    )

    print(
        f"Antisaccade sequence : "
        f"{antisaccade_sequence}"
    )

    # --------------------------------------------------------
    # WINDOW
    # --------------------------------------------------------

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

    left_target = visual.Circle(
        win,
        radius=0.4,
        pos=(
            -PROSACCADE_TARGET_ECCENTRICITY,
            0,
        ),
        fillColor="black",
        lineColor="black",
    )

    right_target = visual.Circle(
        win,
        radius=0.4,
        pos=(
            PROSACCADE_TARGET_ECCENTRICITY,
            0,
        ),
        fillColor="black",
        lineColor="black",
    )

    rest_stimulus = visual.TextStim(
        win,
        text="Rest",
        pos=(0, 0),
        height=0.8,
        color="black",
    )

    instruction_stimulus = visual.TextStim(
        win,
        text="",
        pos=(0, 0),
        height=0.6,
        color="black",
        wrapWidth=24,
    )

    # Allow PsychoPy window to settle.
    for _ in range(30):
        win.flip()

    # --------------------------------------------------------
    # START ONE CONTINUOUS GAZE WORKER
    # --------------------------------------------------------

    running = True

    worker = threading.Thread(
        target=gaze_worker,
        daemon=True,
    )

    worker.start()

    gaze_ready = wait_for_gaze_ready(
        min_samples=10,
        timeout=10.0,
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

    # --------------------------------------------------------
    # FIXATION SMOKE BLOCK
    # --------------------------------------------------------

    print(
        "\nStarting fixation smoke block..."
    )

    fixation.draw()

    win.callOnFlip(
        record_stimulus_event,
        "fixation_onset",
        "fixation",
        block=1,
    )

    win.flip()

    fixation_timer = core.Clock()

    while (
        fixation_timer.getTime()
        < SMOKE_FIXATION_DURATION
    ):

        if escape_pressed():
            aborted = True
            break

        fixation.draw()
        win.flip()

    if not aborted:

        fixation.draw()

        win.callOnFlip(
            record_stimulus_event,
            "fixation_offset",
            "fixation",
            block=1,
        )

        win.flip()

    # --------------------------------------------------------
    # PROSACCADE
    # --------------------------------------------------------

    if not aborted:

        instruction_stimulus.text = (
            "PROSACCADE\n\n"
            "Look at the dot as quickly as you can "
            "when it appears.\n\n"
            "Press SPACE to continue."
        )

        instruction_stimulus.draw()
        win.flip()

        keys = event.waitKeys(
            keyList=[
                "space",
                "escape",
            ]
        )

        if "escape" in keys:
            aborted = True

    if not aborted:

        for trial_number, (
            direction,
            iti_duration,
        ) in enumerate(
            zip(
                prosaccade_sequence,
                prosaccade_iti,
            ),
            start=1,
        ):

            print(
                f"Prosaccade trial "
                f"{trial_number}: "
                f"{direction.upper()}"
            )

            aborted = (
                run_prosaccade_trial(
                    win=win,
                    fixation=fixation,
                    left_target=left_target,
                    right_target=right_target,
                    trial_number=trial_number,
                    direction=direction,
                    iti_duration=iti_duration,
                )
            )

            if aborted:
                break

    # --------------------------------------------------------
    # TRANSITION
    # --------------------------------------------------------

    if not aborted:

        rest_stimulus.text = (
            "Short rest\n\n"
            "Next: Antisaccade\n\n"
            "Press SPACE when ready."
        )

        rest_stimulus.draw()
        win.flip()

        keys = event.waitKeys(
            keyList=[
                "space",
                "escape",
            ]
        )

        if "escape" in keys:
            aborted = True

    # --------------------------------------------------------
    # ANTISACCADE
    # --------------------------------------------------------

    if not aborted:

        instruction_stimulus.text = (
            "ANTISACCADE\n\n"
            "Start each trial looking at the center (+).\n\n"
            "Dot LEFT  -> look to the empty RIGHT side.\n"
            "Dot RIGHT -> look to the empty LEFT side.\n\n"
            "Do NOT look at the dot.\n\n"
            "Press SPACE to continue."
        )

        instruction_stimulus.draw()
        win.flip()

        keys = event.waitKeys(
            keyList=[
                "space",
                "escape",
            ]
        )

        if "escape" in keys:
            aborted = True

    if not aborted:

        for trial_number, (
            direction,
            iti_duration,
        ) in enumerate(
            zip(
                antisaccade_sequence,
                antisaccade_iti,
            ),
            start=1,
        ):

            print(
                f"Antisaccade trial "
                f"{trial_number}: "
                f"{direction.upper()}"
            )

            aborted = (
                run_antisaccade_trial(
                    win=win,
                    fixation=fixation,
                    left_target=left_target,
                    right_target=right_target,
                    trial_number=trial_number,
                    direction=direction,
                    iti_duration=iti_duration,
                )
            )

            if aborted:
                break

    # --------------------------------------------------------
    # STOP THE SAME GAZE WORKER
    # --------------------------------------------------------

    running = False

    worker.join(
        timeout=2.0
    )

    win.close()

    # --------------------------------------------------------
    # SAVE ONE CONTINUOUS SESSION
    # --------------------------------------------------------

    gaze_path, event_path = (
        save_combined_data()
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

    task_counts = {}

    for stimulus_event in stimulus_events:

        task = stimulus_event[
            "task"
        ]

        task_counts[task] = (
            task_counts.get(
                task,
                0,
            )
            + 1
        )

    print(
        "\n"
        + "=" * 60
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
        f"Events by task      : "
        f"{task_counts}"
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
        "=" * 60
    )


if __name__ == "__main__":
    main()