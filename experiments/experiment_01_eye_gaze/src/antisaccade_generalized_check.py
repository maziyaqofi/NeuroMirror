from pathlib import Path

from psychopy import visual, monitors, core, event

from event_logger import EventLogger, generate_log_filename


MONITOR_NAME = "neuromirror_macbook"

FIXATION_DURATION = 1.0
TARGET_DURATION = 1.0
ITI_DURATION = 1.0

TARGET_ECCENTRICITY = 10.0
TARGET_DIRECTION = "right"

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def escape_pressed():
    return "escape" in event.getKeys()


def wait_with_stimulus(win, stimulus, duration):
    timer = core.Clock()

    while timer.getTime() < duration:

        if escape_pressed():
            return True

        stimulus.draw()
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


def main():
    print("=" * 50)
    print("NeuroMirror Experiment 01")
    print("Phase 1C.23 — Generalized Antisaccade Trial")
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

    # -----------------------------------------
    # INSTRUCTION
    # -----------------------------------------

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

    # -----------------------------------------
    # STIMULI
    # -----------------------------------------

    fixation = visual.TextStim(
        win,
        text="+",
        pos=(0, 0),
        height=1.0,
        color="black"
    )

    left_target = visual.Circle(
        win,
        radius=0.4,
        pos=(-10.0, 0),
        fillColor="black",
        lineColor="black"
    )

    right_target = visual.Circle(
        win,
        radius=0.4,
        pos=(10.0, 0),
        fillColor="black",
        lineColor="black"
    )

    TEST_DIRECTION = "left"

    trial_config = get_antisaccade_trial_config(
        direction=TEST_DIRECTION,
        left_target=left_target,
        right_target=right_target
    )

    target = trial_config["target"]
    target_direction = trial_config["target_direction"]
    target_eccentricity = trial_config["target_eccentricity_deg"]
    expected_response = trial_config["expected_response_direction"]

    print("\nTrial configuration:")
    print(f"Direction          : {target_direction}")
    print(f"Target position    : {target_eccentricity} deg")
    print(
        f"Expected response  : "
        f"{expected_response.upper()}"
    )
    print(f"Fixation duration  : {FIXATION_DURATION:.1f} s")
    print(f"Target duration    : {TARGET_DURATION:.1f} s")
    print(f"ITI duration       : {ITI_DURATION:.1f} s")

    # -----------------------------------------
    # CLOCK + LOGGER
    # -----------------------------------------

    experiment_clock = core.Clock()

    logger = EventLogger(
        experiment_clock=experiment_clock
    )

    # -----------------------------------------
    # SHOW INSTRUCTION
    # -----------------------------------------

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

    # -----------------------------------------
    # FIXATION
    # -----------------------------------------

    fixation.draw()

    win.callOnFlip(
        logger.log_event,
        event_type="fixation_onset",
        task="antisaccade",
        trial=1
    )

    win.flip()

    aborted = wait_with_stimulus(
        win,
        fixation,
        FIXATION_DURATION
    )

    if not aborted:

        # -----------------------------------------
        # PERIPHERAL TARGET
        # -----------------------------------------

        target.draw()

        win.callOnFlip(
            logger.log_event,
            event_type="target_onset",
            task="antisaccade",
            trial=1,
            intended_iti_s=ITI_DURATION
        )

        win.flip()

        aborted = wait_with_stimulus(
            win,
            target,
            TARGET_DURATION
        )

    if not aborted:

        # -----------------------------------------
        # TARGET OFFSET + ITI
        # -----------------------------------------

        win.callOnFlip(
            logger.log_event,
            event_type="target_offset",
            task="antisaccade",
            trial=1,
            intended_iti_s=ITI_DURATION
        )

        win.callOnFlip(
            logger.log_event,
            event_type="iti_onset",
            task="antisaccade",
            trial=1
        )

        # Blank frame
        win.flip()

        timer = core.Clock()

        while timer.getTime() < ITI_DURATION:

            if escape_pressed():
                aborted = True
                break

            win.flip()

    if aborted:

        logger.log_event(
            event_type="experiment_abort",
            task="antisaccade",
            trial=1,
            details="escape_pressed"
        )

    else:

        win.callOnFlip(
            logger.log_event,
            event_type="iti_offset",
            task="antisaccade",
            trial=1
        )

        win.flip()

        logger.log_event(
            event_type="experiment_end",
            task="antisaccade"
        )

    # -----------------------------------------
    # CLOSE + SAVE
    # -----------------------------------------

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


if __name__ == "__main__":
    main()