"""
NeuroMirror Phase 1G.4
Full-Session Runner

Purpose
-------
Integrate the complete Experiment 01 session flow into one continuous
development session using:

- one PsychoPy window,
- one camera / MediaPipe worker,
- one shared experiment clock,
- one continuous gaze stream,
- and one unified event timeline.

This is an engineering development runner.

It does not diagnose Alzheimer's disease, MCI, or any other clinical
condition.
"""

from datetime import datetime
from pathlib import Path
import argparse
import csv
import sys
import threading

# ============================================================
# PROTECT RUNNER CLI ARGUMENTS FROM PSYCHOPY
# ============================================================

_RUNNER_ARGV = sys.argv[1:]

if __name__ == "__main__":
    sys.argv = [sys.argv[0]]

from psychopy import visual, monitors, core, event

import combined_task_gaze_check as shared
from randomization import (
    generate_balanced_sequence,
    generate_random_iti_sequence,
)


# ============================================================
# SESSION CONFIGURATION
# ============================================================

MONITOR_NAME = shared.MONITOR_NAME

WINDOW_SIZE = (
    1440,
    900,
)

CALIBRATION_TARGET_DURATION = 2.0
VALIDATION_TARGET_DURATION = 2.0

FIXATION_DURATION = 10.0
FIXATION_REST_DURATION = 3.0
FIXATION_BLOCKS = 3

PROSACCADE_TRIALS_PER_DIRECTION = 10
ANTISACCADE_TRIALS_PER_DIRECTION = 10

PARTICIPANT_ID = "NM01"
STUDY_DAY = None

PROSACCADE_SEED = None
ANTISACCADE_SEED = None
PROSACCADE_ITI_SEED = None
ANTISACCADE_ITI_SEED = None

PROJECT_ROOT = Path(__file__).resolve().parents[3]

RANDOMIZATION_SCHEDULE = (
    Path(__file__).resolve().parents[1]
    / "config"
    / "randomization_schedule_v1.csv"
)

OUTPUT_DIR = None


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
# FULL-SESSION EVENT LOGGER
# ============================================================

def record_event(
    event_type,
    phase,
    block=None,
    trial=None,
    point_name=None,
    target_direction=None,
    expected_response_direction=None,
    target_x_deg=None,
    target_y_deg=None,
    planned_iti_s=None,
):
    """
    Record an event using the shared experiment clock.

    When visual timing matters, this function should be called
    through win.callOnFlip().
    """

    event_record = {
        "timestamp":
            shared.experiment_clock.getTime(),

        "event_type":
            event_type,

        "phase":
            phase,

        "block":
            block,

        "trial":
            trial,

        "point_name":
            point_name,

        "target_direction":
            target_direction,

        "expected_response_direction":
            expected_response_direction,

        "target_x_deg":
            target_x_deg,

        "target_y_deg":
            target_y_deg,

        "planned_iti_s":
            planned_iti_s,
    }

    with shared.data_lock:

        shared.stimulus_events.append(
            event_record
        )


# ============================================================
# CALIBRATION / VALIDATION PRESENTATION
# ============================================================

def present_target_sequence(
    win,
    target_stimulus,
    points,
    phase,
    target_duration,
):
    """
    Present calibration or validation targets while the same
    background gaze worker remains active.
    """

    for (
        point_name,
        target_x,
        target_y,
    ) in points:

        if shared.escape_pressed():
            return False

        target_stimulus.pos = (
            target_x,
            target_y,
        )

        target_stimulus.draw()

        win.callOnFlip(
            record_event,
            "target_onset",
            phase,
            point_name=point_name,
            target_x_deg=target_x,
            target_y_deg=target_y,
        )

        win.flip()

        print(
            f"{phase.upper():<11} "
            f"{point_name:<14} "
            f"X={target_x:+5.1f} "
            f"Y={target_y:+5.1f}"
        )

        timer = core.Clock()

        while (
            timer.getTime()
            < target_duration
        ):

            if shared.escape_pressed():
                return False

            target_stimulus.draw()
            win.flip()

        win.callOnFlip(
            record_event,
            "target_offset",
            phase,
            point_name=point_name,
            target_x_deg=target_x,
            target_y_deg=target_y,
        )

        win.flip()

    return True


# ============================================================
# FIXATION BLOCK
# ============================================================

def run_fixation_block(
    win,
    fixation_stimulus,
    block_number,
):
    """
    Run one 10-second fixation block.
    """

    fixation_stimulus.draw()

    win.callOnFlip(
        record_event,
        "fixation_onset",
        "fixation",
        block=block_number,
    )

    win.flip()

    timer = core.Clock()

    while (
        timer.getTime()
        < FIXATION_DURATION
    ):

        if shared.escape_pressed():
            return False

        fixation_stimulus.draw()
        win.flip()

    fixation_stimulus.draw()

    win.callOnFlip(
        record_event,
        "fixation_offset",
        "fixation",
        block=block_number,
    )

    win.flip()

    return True


def run_fixation_rest(
    win,
    rest_stimulus,
    block_number,
):
    """
    Run the protocol-defined 3-second rest between fixation blocks.
    """

    rest_stimulus.draw()

    win.callOnFlip(
        record_event,
        "rest_onset",
        "fixation",
        block=block_number,
    )

    win.flip()

    timer = core.Clock()

    while (
        timer.getTime()
        < FIXATION_REST_DURATION
    ):

        if shared.escape_pressed():
            return False

        rest_stimulus.draw()
        win.flip()

    win.callOnFlip(
        record_event,
        "rest_offset",
        "fixation",
        block=block_number,
    )

    win.flip()

    return True


# ============================================================
# INSTRUCTION SCREEN
# ============================================================

def wait_for_space(
    win,
    stimulus,
    text,
):
    stimulus.text = text
    stimulus.draw()
    win.flip()

    keys = event.waitKeys(
        keyList=[
            "space",
            "escape",
        ]
    )

    return (
        "escape"
        not in keys
    )

# ============================================================
# SACCADE TASK HELPERS
# ============================================================

def hold_stimulus(
    win,
    stimulus,
    duration,
):
    timer = core.Clock()

    while timer.getTime() < duration:

        if shared.escape_pressed():
            return False

        stimulus.draw()
        win.flip()

    return True


def hold_blank(
    win,
    duration,
):
    timer = core.Clock()

    while timer.getTime() < duration:

        if shared.escape_pressed():
            return False

        win.flip()

    return True


# ============================================================
# PROSACCADE
# ============================================================

def run_prosaccade_trial(
    win,
    fixation,
    left_target,
    right_target,
    trial_number,
    direction,
    iti_duration,
):

    if direction == "right":
        target = right_target
        eccentricity = +10.0
    else:
        target = left_target
        eccentricity = -10.0

    fixation.draw()

    win.callOnFlip(
        record_event,
        "fixation_onset",
        "prosaccade",
        trial=trial_number,
        target_direction=direction,
        target_x_deg=eccentricity,
        target_y_deg=0.0,
        planned_iti_s=iti_duration,
    )

    win.flip()

    if not hold_stimulus(
        win,
        fixation,
        1.0,
    ):
        return False

    target.draw()

    win.callOnFlip(
        record_event,
        "target_onset",
        "prosaccade",
        trial=trial_number,
        target_direction=direction,
        target_x_deg=eccentricity,
        target_y_deg=0.0,
        planned_iti_s=iti_duration,
    )

    win.flip()

    if not hold_stimulus(
        win,
        target,
        1.0,
    ):
        return False

    win.callOnFlip(
        record_event,
        "target_offset",
        "prosaccade",
        trial=trial_number,
        target_direction=direction,
        target_x_deg=eccentricity,
        target_y_deg=0.0,
        planned_iti_s=iti_duration,
    )

    win.callOnFlip(
        record_event,
        "iti_onset",
        "prosaccade",
        trial=trial_number,
        target_direction=direction,
        target_x_deg=eccentricity,
        target_y_deg=0.0,
        planned_iti_s=iti_duration,
    )

    win.flip()

    if not hold_blank(
        win,
        iti_duration,
    ):
        return False

    win.callOnFlip(
        record_event,
        "iti_offset",
        "prosaccade",
        trial=trial_number,
        target_direction=direction,
        target_x_deg=eccentricity,
        target_y_deg=0.0,
        planned_iti_s=iti_duration,
    )

    win.flip()

    return True


# ============================================================
# ANTISACCADE
# ============================================================

def run_antisaccade_trial(
    win,
    fixation,
    left_target,
    right_target,
    trial_number,
    direction,
    iti_duration,
):

    if direction == "right":
        target = right_target
        eccentricity = +10.0
        expected_direction = "left"
    else:
        target = left_target
        eccentricity = -10.0
        expected_direction = "right"

    fixation.draw()

    win.callOnFlip(
        record_event,
        "fixation_onset",
        "antisaccade",
        trial=trial_number,
        target_direction=direction,
        expected_response_direction=expected_direction,
        target_x_deg=eccentricity,
        target_y_deg=0.0,
        planned_iti_s=iti_duration,
    )

    win.flip()

    if not hold_stimulus(
        win,
        fixation,
        1.0,
    ):
        return False

    target.draw()

    win.callOnFlip(
        record_event,
        "target_onset",
        "antisaccade",
        trial=trial_number,
        target_direction=direction,
        expected_response_direction=expected_direction,
        target_x_deg=eccentricity,
        target_y_deg=0.0,
        planned_iti_s=iti_duration,
    )

    win.flip()

    if not hold_stimulus(
        win,
        target,
        1.0,
    ):
        return False

    win.callOnFlip(
        record_event,
        "target_offset",
        "antisaccade",
        trial=trial_number,
        target_direction=direction,
        expected_response_direction=expected_direction,
        target_x_deg=eccentricity,
        target_y_deg=0.0,
        planned_iti_s=iti_duration,
    )

    win.callOnFlip(
        record_event,
        "iti_onset",
        "antisaccade",
        trial=trial_number,
        target_direction=direction,
        expected_response_direction=expected_direction,
        target_x_deg=eccentricity,
        target_y_deg=0.0,
        planned_iti_s=iti_duration,
    )

    win.flip()

    if not hold_blank(
        win,
        iti_duration,
    ):
        return False

    win.callOnFlip(
        record_event,
        "iti_offset",
        "antisaccade",
        trial=trial_number,
        target_direction=direction,
        expected_response_direction=expected_direction,
        target_x_deg=eccentricity,
        target_y_deg=0.0,
        planned_iti_s=iti_duration,
    )

    win.flip()

    return True

# ============================================================
# EXPERIMENT SESSION CONFIGURATION
# ============================================================

def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "NeuroMirror Experiment 01 "
            "14-Day Eye/Gaze Session Runner"
        )
    )

    parser.add_argument(
        "--day",
        type=int,
        required=True,
        choices=range(1, 15),
        metavar="1-14",
        help="Experiment study day (1-14).",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Use the experiment runner configuration "
            "without writing into the official "
            "Experiment 01 dataset."
        ),
    )

    return parser.parse_args(
        _RUNNER_ARGV
    )


def load_randomization_for_day(study_day):

    if not RANDOMIZATION_SCHEDULE.exists():
        raise FileNotFoundError(
            "Randomization schedule not found: "
            f"{RANDOMIZATION_SCHEDULE}"
        )

    with RANDOMIZATION_SCHEDULE.open(
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            if int(row["study_day"]) == study_day:

                return {
                    "prosaccade_seed": int(
                        row["prosaccade_seed"]
                    ),
                    "prosaccade_iti_seed": int(
                        row["prosaccade_iti_seed"]
                    ),
                    "antisaccade_seed": int(
                        row["antisaccade_seed"]
                    ),
                    "antisaccade_iti_seed": int(
                        row["antisaccade_iti_seed"]
                    ),
                }

    raise ValueError(
        f"No randomization entry for Day {study_day}."
    )


def configure_experiment_session(
    study_day,
    dry_run=False,
):
    global STUDY_DAY
    global PROSACCADE_SEED
    global ANTISACCADE_SEED
    global PROSACCADE_ITI_SEED
    global ANTISACCADE_ITI_SEED
    global OUTPUT_DIR

    STUDY_DAY = study_day

    seeds = load_randomization_for_day(
        study_day
    )

    PROSACCADE_SEED = seeds[
        "prosaccade_seed"
    ]

    PROSACCADE_ITI_SEED = seeds[
        "prosaccade_iti_seed"
    ]

    ANTISACCADE_SEED = seeds[
        "antisaccade_seed"
    ]

    ANTISACCADE_ITI_SEED = seeds[
        "antisaccade_iti_seed"
    ]

    if dry_run:
        OUTPUT_DIR = (
            PROJECT_ROOT
            / "data"
            / "raw"
            / "dry_run"
            / f"day_{study_day:02d}"
        )
    else:
        OUTPUT_DIR = (
            PROJECT_ROOT
            / "data"
            / "raw"
            / "experiment_01"
            / f"day_{study_day:02d}"
        )

    return seeds


def guard_existing_official_session(
    study_day,
):
    day_directory = (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "experiment_01"
        / f"day_{study_day:02d}"
    )

    if not day_directory.exists():
        return

    existing_files = list(
        day_directory.glob(
            f"{PARTICIPANT_ID}_D"
            f"{study_day:02d}_*.csv"
        )
    )

    if existing_files:
        print(
            "\nERROR: Official data already exist "
            f"for Experiment Day {study_day:02d}."
        )

        print(
            "Existing raw data will not be "
            "overwritten automatically."
        )

        print(
            "If this represents an aborted or "
            "repeated session, document the "
            "protocol deviation before proceeding."
        )

        sys.exit(1)

# ============================================================
# FULL-SESSION DATA SAVING
# ============================================================

def save_session_data(
    session_timestamp,
    session_status,
    dry_run=False,
):
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    prefix = (
        f"{PARTICIPANT_ID}_"
        f"D{STUDY_DAY:02d}"
    )

    gaze_path = OUTPUT_DIR / (
        f"{prefix}_gaze_"
        f"{session_timestamp}.csv"
    )

    event_path = OUTPUT_DIR / (
        f"{prefix}_events_"
        f"{session_timestamp}.csv"
    )

    metadata_path = OUTPUT_DIR / (
        f"{prefix}_metadata_"
        f"{session_timestamp}.csv"
    )

    with shared.data_lock:
        gaze_data = list(
            shared.gaze_samples
        )

        event_data = list(
            shared.stimulus_events
        )

    gaze_fieldnames = [
        "timestamp",
        "frame_number",
        "face_detected",
        "left_iris_ratio",
        "right_iris_ratio",
        "average_iris_ratio",
    ]

    event_fieldnames = [
        "timestamp",
        "event_type",
        "phase",
        "block",
        "trial",
        "point_name",
        "target_direction",
        "expected_response_direction",
        "target_x_deg",
        "target_y_deg",
        "planned_iti_s",
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
        writer.writerows(gaze_data)

    with event_path.open(
        "w",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=event_fieldnames,
        )

        writer.writeheader()
        writer.writerows(event_data)

    total_samples = len(gaze_data)

    detected_samples = sum(
        int(row["face_detected"])
        for row in gaze_data
    )

    detection_rate = (
        100.0
        * detected_samples
        / total_samples
        if total_samples
        else 0.0
    )

    measured_fps = 0.0

    if len(gaze_data) >= 2:
        first_time = float(
            gaze_data[0]["timestamp"]
        )
        last_time = float(
            gaze_data[-1]["timestamp"]
        )

        duration = last_time - first_time

        if duration > 0:
            measured_fps = (
                (len(gaze_data) - 1)
                / duration
            )

    metadata = {
        "participant_id": PARTICIPANT_ID,
        "study_day": STUDY_DAY,
        "session_id": (
            f"{PARTICIPANT_ID}_"
            f"D{STUDY_DAY:02d}_"
            f"{session_timestamp}"
        ),
        "session_datetime": (
            datetime.now().isoformat(
                timespec="seconds"
            )
        ),
        "protocol_version": "1.0",
        "dry_run": dry_run,
        "viewing_distance_cm": 52.5,
        "camera_device": (
            "Built-in FaceTime HD RGB camera"
        ),
        "requested_camera_resolution": (
            "1280x720"
        ),
        "requested_camera_fps": 30,
        "measured_camera_fps": (
            f"{measured_fps:.4f}"
        ),
        "display_resolution": (
            f"{WINDOW_SIZE[0]}x"
            f"{WINDOW_SIZE[1]}"
        ),
        "prosaccade_seed": (
            PROSACCADE_SEED
        ),
        "prosaccade_iti_seed": (
            PROSACCADE_ITI_SEED
        ),
        "antisaccade_seed": (
            ANTISACCADE_SEED
        ),
        "antisaccade_iti_seed": (
            ANTISACCADE_ITI_SEED
        ),
        "session_status": session_status,
        "gaze_samples": total_samples,
        "face_detection_rate": (
            f"{detection_rate:.4f}"
        ),
        "notes": "",
    }

    with metadata_path.open(
        "w",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=list(
                metadata.keys()
            ),
        )

        writer.writeheader()
        writer.writerow(metadata)

    return (
        gaze_path,
        event_path,
        metadata_path,
    )


# ============================================================
# MAIN FULL-SESSION CONTROLLER
# ============================================================

def main(dry_run=False):

    print(
        "\n=== NeuroMirror Phase 1G.4 "
        "— Full-Session Runner ===\n"
    )

    session_timestamp = (
        datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
    )

    # --------------------------------------------------------
    # RESET SHARED SESSION STATE
    # --------------------------------------------------------

    with shared.data_lock:

        shared.gaze_samples.clear()
        shared.stimulus_events.clear()

    shared.experiment_clock.reset()

    # --------------------------------------------------------
    # RANDOMIZATION
    # --------------------------------------------------------

    prosaccade_sequence, prosaccade_attempts = (
        generate_balanced_sequence(
            trials_per_direction=(
                PROSACCADE_TRIALS_PER_DIRECTION
            ),
            max_consecutive=3,
            seed=PROSACCADE_SEED,
        )
    )

    prosaccade_iti = (
        generate_random_iti_sequence(
            num_trials=20,
            min_duration=(
                shared.PROSACCADE_MIN_ITI
            ),
            max_duration=(
                shared.PROSACCADE_MAX_ITI
            ),
            seed=PROSACCADE_ITI_SEED,
        )
    )

    antisaccade_sequence, antisaccade_attempts = (
        generate_balanced_sequence(
            trials_per_direction=(
                ANTISACCADE_TRIALS_PER_DIRECTION
            ),
            max_consecutive=3,
            seed=ANTISACCADE_SEED,
        )
    )

    antisaccade_iti = (
        generate_random_iti_sequence(
            num_trials=20,
            min_duration=(
                shared.ANTISACCADE_MIN_ITI
            ),
            max_duration=(
                shared.ANTISACCADE_MAX_ITI
            ),
            seed=ANTISACCADE_ITI_SEED,
        )
    )

    print(
        f"Session timestamp     : "
        f"{session_timestamp}"
    )

    print(
        f"Prosaccade seed       : "
        f"{PROSACCADE_SEED}"
    )

    print(
        f"Prosaccade attempts   : "
        f"{prosaccade_attempts}"
    )

    print(
        f"Prosaccade ITI seed   : "
        f"{PROSACCADE_ITI_SEED}"
    )

    print(
        f"Antisaccade seed      : "
        f"{ANTISACCADE_SEED}"
    )

    print(
        f"Antisaccade attempts  : "
        f"{antisaccade_attempts}"
    )

    print(
        f"Antisaccade ITI seed  : "
        f"{ANTISACCADE_ITI_SEED}"
    )

    # --------------------------------------------------------
    # PSYCHOPY WINDOW
    # --------------------------------------------------------

    monitor = monitors.Monitor(
        MONITOR_NAME
    )

    win = visual.Window(
        size=WINDOW_SIZE,
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

    gaze_target = visual.Circle(
        win,
        radius=0.4,
        pos=(0, 0),
        fillColor="black",
        lineColor="black",
    )

    left_target = visual.Circle(
        win,
        radius=0.4,
        pos=(-10.0, 0),
        fillColor="black",
        lineColor="black",
    )

    right_target = visual.Circle(
        win,
        radius=0.4,
        pos=(+10.0, 0),
        fillColor="black",
        lineColor="black",
    )

    rest_stimulus = visual.TextStim(
        win,
        text="+",
        pos=(0, 0),
        height=1.0,
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

    # Allow the window to settle.
    for _ in range(30):
        win.flip()

    # --------------------------------------------------------
    # START ONE CONTINUOUS GAZE WORKER
    # --------------------------------------------------------

    shared.running = True

    worker = threading.Thread(
        target=shared.gaze_worker,
        daemon=True,
    )

    worker.start()

    gaze_ready = shared.wait_for_gaze_ready(
        min_samples=10,
        timeout=10.0,
    )

    if not gaze_ready:

        print(
            "\nERROR: Gaze acquisition did not "
            "become ready within 10 seconds."
        )

        shared.running = False

        worker.join(
            timeout=2.0
        )

        win.close()

        return

    print(
        "\nGaze acquisition ready."
    )

    completed = True

    # --------------------------------------------------------
    # CALIBRATION
    # --------------------------------------------------------

    if completed:

        completed = wait_for_space(
            win,
            instruction_stimulus,
            (
                "CALIBRATION\n\n"
                "Look directly at each target "
                "while it is displayed.\n\n"
                "Keep your head position as stable "
                "as possible.\n\n"
                "Press SPACE to begin."
            ),
        )

    if completed:

        print(
            "\nStarting 9-point calibration..."
        )

        completed = present_target_sequence(
            win=win,
            target_stimulus=gaze_target,
            points=CALIBRATION_POINTS,
            phase="calibration",
            target_duration=(
                CALIBRATION_TARGET_DURATION
            ),
        )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if completed:

        completed = wait_for_space(
            win,
            instruction_stimulus,
            (
                "VALIDATION\n\n"
                "Continue looking directly at "
                "each target.\n\n"
                "Press SPACE to begin."
            ),
        )

    if completed:

        print(
            "\nStarting 4-point validation..."
        )

        completed = present_target_sequence(
            win=win,
            target_stimulus=gaze_target,
            points=VALIDATION_POINTS,
            phase="validation",
            target_duration=(
                VALIDATION_TARGET_DURATION
            ),
        )

    # --------------------------------------------------------
    # FIXATION
    # --------------------------------------------------------

    if completed:

        completed = wait_for_space(
            win,
            instruction_stimulus,
            (
                "FIXATION\n\n"
                "Look at the center (+) and keep "
                "your gaze as steady as possible.\n\n"
                "There will be 3 blocks.\n\n"
                "Press SPACE to begin."
            ),
        )

    if completed:

        print(
            "\nStarting fixation blocks..."
        )

        for block_number in range(
            1,
            FIXATION_BLOCKS + 1,
        ):

            print(
                f"Fixation block "
                f"{block_number}/{FIXATION_BLOCKS}"
            )

            completed = run_fixation_block(
                win=win,
                fixation_stimulus=fixation,
                block_number=block_number,
            )

            if not completed:
                break

            if block_number < FIXATION_BLOCKS:

                completed = run_fixation_rest(
                    win=win,
                    rest_stimulus=rest_stimulus,
                    block_number=block_number,
                )

                if not completed:
                    break

    # --------------------------------------------------------
    # PROSACCADE
    # --------------------------------------------------------

    if completed:

        completed = wait_for_space(
            win,
            instruction_stimulus,
            (
                "PROSACCADE\n\n"
                "Start each trial looking at "
                "the center (+).\n\n"
                "Look at the dot as quickly as "
                "you can when it appears.\n\n"
                "Press SPACE to begin."
            ),
        )

    if completed:

        print(
            "\nStarting 20 prosaccade trials..."
        )

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
                f"Prosaccade "
                f"{trial_number:02d}/20 | "
                f"{direction.upper()}"
            )

            completed = run_prosaccade_trial(
                win=win,
                fixation=fixation,
                left_target=left_target,
                right_target=right_target,
                trial_number=trial_number,
                direction=direction,
                iti_duration=iti_duration,
            )

            if not completed:
                break

    # --------------------------------------------------------
    # ANTISACCADE
    # --------------------------------------------------------

    if completed:

        completed = wait_for_space(
            win,
            instruction_stimulus,
            (
                "ANTISACCADE\n\n"
                "Start each trial looking at "
                "the center (+).\n\n"
                "Dot LEFT  -> look to the empty "
                "RIGHT side.\n"
                "Dot RIGHT -> look to the empty "
                "LEFT side.\n\n"
                "Do NOT look at the dot.\n\n"
                "Press SPACE to begin."
            ),
        )

    if completed:

        print(
            "\nStarting 20 antisaccade trials..."
        )

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
                f"Antisaccade "
                f"{trial_number:02d}/20 | "
                f"{direction.upper()}"
            )

            completed = run_antisaccade_trial(
                win=win,
                fixation=fixation,
                left_target=left_target,
                right_target=right_target,
                trial_number=trial_number,
                direction=direction,
                iti_duration=iti_duration,
            )

            if not completed:
                break

    # --------------------------------------------------------
    # CLEANUP
    # --------------------------------------------------------

    shared.running = False

    worker.join(
        timeout=2.0
    )

    win.close()

    # --------------------------------------------------------
    # SAVE RAW SESSION
    # --------------------------------------------------------

    gaze_path, event_path, metadata_path = (
        save_session_data(
            session_timestamp,
            session_status=(
                "COMPLETED"
                if completed
                else "ABORTED"
            ),
            dry_run=dry_run,
        )
    )

    with shared.data_lock:

        total_samples = len(
            shared.gaze_samples
        )

        detected_samples = sum(
            sample["face_detected"]
            for sample in shared.gaze_samples
        )

        total_events = len(
            shared.stimulus_events
        )

        event_snapshot = list(
            shared.stimulus_events
        )

    detection_rate = (
        detected_samples
        / total_samples
        * 100
        if total_samples
        else 0.0
    )

    phase_counts = {}

    for item in event_snapshot:

        phase = item["phase"]

        phase_counts[phase] = (
            phase_counts.get(
                phase,
                0,
            )
            + 1
        )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print(
        "\n"
        + "=" * 65
    )

    print(
        "Status              : "
        + (
            "COMPLETED"
            if completed
            else "ABORTED"
        )
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
        f"{total_events}"
    )

    print(
        f"Events by phase     : "
        f"{phase_counts}"
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
        f"Metadata   : "
        f"{metadata_path}"
    )

    print(
        "=" * 65
    )


if __name__ == "__main__":

    args = parse_arguments()

    if not args.dry_run:
        guard_existing_official_session(
            args.day
        )

    configure_experiment_session(
        study_day=args.day,
        dry_run=args.dry_run,
    )

    print(
        "\nExperiment configuration"
    )
    print(
        f"Participant : {PARTICIPANT_ID}"
    )
    print(
        f"Study day   : {STUDY_DAY:02d}"
    )
    print(
        f"Dry run     : {args.dry_run}"
    )
    print(
        f"Output      : {OUTPUT_DIR}"
    )

    main(
        dry_run=args.dry_run
    )