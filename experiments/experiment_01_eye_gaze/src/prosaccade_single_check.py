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


def main():
    print("=" * 50)
    print("NeuroMirror Experiment 01")
    print("Phase 1C — Single Prosaccade Trial")
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

    # Central fixation
    fixation = visual.TextStim(
        win,
        text="+",
        pos=(0, 0),
        height=1.0,
        color="black"
    )

    # Peripheral target at +10 degrees.
    target = visual.Circle(
        win,
        radius=0.4,
        pos=(TARGET_ECCENTRICITY, 0),
        fillColor="black",
        lineColor="black"
    )

    experiment_clock = core.Clock()

    logger = EventLogger(
        experiment_clock=experiment_clock
    )

    logger.log_event(
        event_type="experiment_start"
    )

    print("\nTrial configuration:")
    print(f"Direction          : {TARGET_DIRECTION}")
    print(f"Target position    : +{TARGET_ECCENTRICITY} deg")
    print(f"Fixation duration  : {FIXATION_DURATION:.1f} s")
    print(f"Target duration    : {TARGET_DURATION:.1f} s")
    print(f"ITI duration       : {ITI_DURATION:.1f} s")

    # -----------------------------------------
    # FIXATION
    # -----------------------------------------

    fixation.draw()

    win.callOnFlip(
        logger.log_event,
        event_type="fixation_onset",
        task="prosaccade",
        trial=1,
        details="center"
    )

    win.flip()

    aborted = wait_with_stimulus(
        win,
        fixation,
        FIXATION_DURATION
    )

    if aborted:
        logger.log_event(
            event_type="experiment_abort",
            details="escape_pressed"
        )

    else:

        # -----------------------------------------
        # PERIPHERAL TARGET
        # -----------------------------------------

        target.draw()

        win.callOnFlip(
            logger.log_event,
            event_type="target_onset",
            task="prosaccade",
            trial=1,
            details="right_10deg"
        )

        win.flip()

        aborted = wait_with_stimulus(
            win,
            target,
            TARGET_DURATION
        )

    if not aborted:

        # -----------------------------------------
        # ITI / BLANK
        # -----------------------------------------

        win.callOnFlip(
            logger.log_event,
            event_type="target_offset",
            task="prosaccade",
            trial=1,
            details="right_10deg"
        )

        win.callOnFlip(
            logger.log_event,
            event_type="iti_onset",
            task="prosaccade",
            trial=1
        )

        # Nothing is drawn → blank frame.
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
            task="prosaccade",
            trial=1,
            details="escape_pressed"
        )

    else:

        win.callOnFlip(
            logger.log_event,
            event_type="iti_offset",
            task="prosaccade",
            trial=1
        )

        win.flip()

        logger.log_event(
            event_type="experiment_end"
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