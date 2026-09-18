from pathlib import Path

from psychopy import visual, monitors, core, event

from event_logger import EventLogger, generate_log_filename


MONITOR_NAME = "neuromirror_macbook"

FIXATION_DURATION = 1.0
TARGET_DURATION = 1.0
ITI_DURATION = 1.0

TARGET_ECCENTRICITY = 10.0

TRIAL_SEQUENCE = [
    "right",
    "left",
    "right",
    "left",
]

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


def run_trial(
    win,
    fixation,
    left_target,
    right_target,
    logger,
    trial_number,
    direction
):
    # -----------------------------------------
    # CENTRAL FIXATION
    # -----------------------------------------

    fixation.draw()

    win.callOnFlip(
        logger.log_event,
        event_type="fixation_onset",
        task="prosaccade",
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

    if direction == "right":
        target = right_target
        target_details = "right_10deg"

    else:
        target = left_target
        target_details = "left_10deg"

    target.draw()

    win.callOnFlip(
        logger.log_event,
        event_type="target_onset",
        task="prosaccade",
        trial=trial_number,
        details=target_details
    )

    win.flip()

    aborted = hold_stimulus(
        win,
        target,
        TARGET_DURATION
    )

    if aborted:
        return True

    # -----------------------------------------
    # TARGET OFFSET + ITI ONSET
    # -----------------------------------------

    win.callOnFlip(
        logger.log_event,
        event_type="target_offset",
        task="prosaccade",
        trial=trial_number,
        details=target_details
    )

    win.callOnFlip(
        logger.log_event,
        event_type="iti_onset",
        task="prosaccade",
        trial=trial_number
    )

    # Blank frame
    win.flip()

    aborted = hold_blank(
        win,
        ITI_DURATION
    )

    if aborted:
        return True

    # -----------------------------------------
    # ITI OFFSET
    # -----------------------------------------

    win.callOnFlip(
        logger.log_event,
        event_type="iti_offset",
        task="prosaccade",
        trial=trial_number
    )

    win.flip()

    return False


def main():
    print("=" * 50)
    print("NeuroMirror Experiment 01")
    print("Phase 1C — 4-Trial Prosaccade Integration")
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

    logger.log_event(
        event_type="experiment_start",
        task="prosaccade"
    )

    print("\nTrial sequence:")

    for trial_number, direction in enumerate(
        TRIAL_SEQUENCE,
        start=1
    ):
        print(
            f"Trial {trial_number}: "
            f"{direction.upper()}"
        )

    aborted = False

    for trial_number, direction in enumerate(
        TRIAL_SEQUENCE,
        start=1
    ):
        print(
            f"\nStarting trial {trial_number} "
            f"({direction.upper()})..."
        )

        aborted = run_trial(
            win=win,
            fixation=fixation,
            left_target=left_target,
            right_target=right_target,
            logger=logger,
            trial_number=trial_number,
            direction=direction
        )

        if aborted:
            logger.log_event(
                event_type="experiment_abort",
                task="prosaccade",
                trial=trial_number,
                details="escape_pressed"
            )
            break

    if not aborted:
        logger.log_event(
            event_type="experiment_end",
            task="prosaccade"
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


if __name__ == "__main__":
    main()