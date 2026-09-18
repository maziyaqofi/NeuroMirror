from pathlib import Path

from psychopy import visual, monitors, core, event

from event_logger import EventLogger, generate_log_filename

from randomization import (
    generate_balanced_sequence,
    generate_random_iti_sequence
)

MONITOR_NAME = "neuromirror_macbook"

FIXATION_DURATION = 1.0
TARGET_DURATION = 1.0
MIN_ITI = 1.0
MAX_ITI = 1.5

TARGET_ECCENTRICITY = 10.0

TEST_SEED = 20260918

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def escape_pressed():
    return "escape" in event.getKeys()


def hold_stimulus(win, stimulus, duration):
    timer = core.Clock()

    while timer.getTime() < duration:

        if escape_pressed():
            return True

        stimulus.draw()
        win.flip()

    return False


def hold_blank(win, duration):
    timer = core.Clock()

    while timer.getTime() < duration:

        if escape_pressed():
            return True

        win.flip()

    return False

def get_antisaccade_trial_config(
    direction,
    left_target,
    right_target
):
    direction = direction.lower()

    if direction == "right":
        return {
            "target": right_target,
            "target_direction": "right",
            "target_eccentricity_deg": 10.0,
            "expected_response_direction": "left",
        }

    elif direction == "left":
        return {
            "target": left_target,
            "target_direction": "left",
            "target_eccentricity_deg": -10.0,
            "expected_response_direction": "right",
        }

    else:
        raise ValueError(
            f"Invalid direction: {direction}"
        )

def run_trial(
    win,
    fixation,
    left_target,
    right_target,
    logger,
    trial_number,
    direction,
    iti_duration
):
    # -----------------------------------------
    # CENTRAL FIXATION
    # -----------------------------------------

    fixation.draw()

    win.callOnFlip(
        logger.log_event,
        event_type="fixation_onset",
        task="antisaccade",
        trial=trial_number,
        details="center"
    )

    win.flip()

    aborted = hold_stimulus(
        win,
        fixation,
        FIXATION_DURATION
    )

    if aborted:
        return True

    # -----------------------------------------
    # PERIPHERAL TARGET
    # -----------------------------------------

    trial_config = get_antisaccade_trial_config(
        direction=direction,
        left_target=left_target,
        right_target=right_target
    )

    target = trial_config["target"]
    target_direction = trial_config["target_direction"]
    target_eccentricity = trial_config[
        "target_eccentricity_deg"
    ]
    expected_response = trial_config[
        "expected_response_direction"
    ]

    # --------------------------------------------------
    # Target phase
    # --------------------------------------------------

    target.draw()

    win.callOnFlip(
        logger.log_event,
        event_type="target_onset",
        task="antisaccade",
        trial=trial_number,
        target_direction=target_direction,
        target_eccentricity_deg=target_eccentricity,
        intended_iti_s=iti_duration,
        details=f"expected_response={expected_response}"
    )

    win.flip()

    target_clock = core.Clock()

    while target_clock.getTime() < TARGET_DURATION:
        keys = event.getKeys()

        if "escape" in keys:
            logger.log_event(
                event_type="experiment_abort",
                task="antisaccade",
                trial=trial_number,
                details="escape_pressed"
            )
            return True

    # --------------------------------------------------
    # Target offset + ITI onset
    # --------------------------------------------------

    win.callOnFlip(
        logger.log_event,
        event_type="target_offset",
        task="antisaccade",
        trial=trial_number,
        target_direction=target_direction,
        target_eccentricity_deg=target_eccentricity,
        intended_iti_s=iti_duration,
        details=f"expected_response={expected_response}"
    )

    win.callOnFlip(
        logger.log_event,
        event_type="iti_onset",
        task="antisaccade",
        trial=trial_number,
        intended_iti_s=iti_duration
    )

    win.flip()

    # -----------------------------------------
    # INTER-TRIAL INTERVAL
    # -----------------------------------------

    iti_clock = core.Clock()

    while iti_clock.getTime() < iti_duration:
        keys = event.getKeys()

        if "escape" in keys:
            logger.log_event(
                event_type="experiment_abort",
                task="antisaccade",
                trial=trial_number,
                details="escape_pressed"
            )
            return True

    # -----------------------------------------
    # ITI OFFSET
    # -----------------------------------------

    win.callOnFlip(
        logger.log_event,
        event_type="iti_offset",
        task="antisaccade",
        trial=trial_number,
        intended_iti_s=iti_duration
    )

    win.flip()

    return False


def main():
    print("=" * 50)
    print("NeuroMirror Experiment 01")
    print("Phase 1C.25 — Full 20-Trial Antisaccade Block")
    print("=" * 50)

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

    instruction = visual.TextStim(
        win,
        text=(
            "Keep looking at the center.\n\n"
            "When a dot appears on one side,\n"
            "look in the OPPOSITE direction.\n\n"
            "Do not look at the dot.\n\n"
            "Press SPACE to begin."
        ),
        color="black",
        height=0.6,
        units="deg"
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
        pos=(TARGET_ECCENTRICITY, 0),
        fillColor="black",
        lineColor="black"
    )

    left_target = visual.Circle(
        win,
        radius=0.4,
        pos=(-TARGET_ECCENTRICITY, 0),
        fillColor="black",
        lineColor="black"
    )

    experiment_clock = core.Clock()

    logger = EventLogger(
        experiment_clock=experiment_clock
    )

    instruction.draw()
    win.flip()

    keys = event.waitKeys(
        keyList=["space", "escape"]
    )

    if "escape" in keys:
        win.close()
        core.quit()

    logger.log_event(
        event_type="experiment_start",
        task="antisaccade"
    )

    trial_sequence, attempts = generate_balanced_sequence(
        trials_per_direction=10,
        max_consecutive=3,
        seed=TEST_SEED
    )

    iti_sequence = generate_random_iti_sequence(
        num_trials=20,
        min_duration=1.0,
        max_duration=1.5,
        seed=TEST_SEED
    )

    print(f"\nRandom seed       : {TEST_SEED}")
    print(f"Generation attempts: {attempts}")

    print("\nTrial sequence:")

    for trial_number, (direction, iti_duration) in enumerate(
        zip(trial_sequence, iti_sequence),
        start=1
    ):
        print(
            f"Trial {trial_number}: "
            f"{direction.upper()}"
        )

    aborted = False

    for trial_number, (direction, iti_duration) in enumerate(
        zip(trial_sequence, iti_sequence),
        start=1
    ):
        print(
            f"\nStarting trial {trial_number} "
            f"({direction.upper()}) | "
            f"ITI={iti_duration:.4f}s"
        )

        aborted = run_trial(
            win=win,
            fixation=fixation,
            left_target=left_target,
            right_target=right_target,
            logger=logger,
            trial_number=trial_number,
            direction=direction,
            iti_duration=iti_duration
        )

        if aborted:
            logger.log_event(
                event_type="experiment_abort",
                task="antisaccade",
                trial=trial_number,
                details="escape_pressed"
            )
            break

    if not aborted:
        logger.log_event(
            event_type="experiment_end",
            task="antisaccade"
        )

    win.close()

    filename = generate_log_filename()

    output_path = (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "development"
        / filename
    )

    logger.save_csv(output_path)

    print("\n" + "=" * 50)

    if aborted:
        print("Status       : ABORTED BY USER")
    else:
        print("Status       : COMPLETED")

    print(f"Total events : {len(logger.events)}")

    print("\nTrial sequence:")
    print("-" * 65)

    for trial_number, (direction, iti_duration) in enumerate(
        zip(trial_sequence, iti_sequence),
        start=1
    ):
        expected_response = (
            "left"
            if direction == "right"
            else "right"
        )

        print(
            f"Trial {trial_number:02d} | "
            f"Target={direction.upper():5s} | "
            f"Expected={expected_response.upper():5s} | "
            f"ITI={iti_duration:.4f}s"
        )

    print("-" * 65)


if __name__ == "__main__":
    main()