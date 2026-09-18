from pathlib import Path

from psychopy import visual, monitors, core, event

from event_logger import EventLogger, generate_log_filename


MONITOR_NAME = "neuromirror_macbook"

FIXATION_DURATION = 1.0
TARGET_DURATION = 1.0
ITI_DURATION = 1.0

TARGET_ECCENTRICITY = -10.0
TARGET_DIRECTION = "left"

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
    print("Phase 1C.21 — Single Antisaccade Trial")
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

    target = visual.Circle(
        win,
        radius=0.4,
        pos=(TARGET_ECCENTRICITY, 0),
        fillColor="black",
        lineColor="black"
    )

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

    print("\nTrial configuration:")
    print(f"Direction          : {TARGET_DIRECTION}")
    print(f"Target position    : {TARGET_ECCENTRICITY} deg")
    print(f"Expected response  : RIGHT")
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
            target_direction="left",
            target_eccentricity_deg=-10.0,
            intended_iti_s=ITI_DURATION,
            details="expected_response=right"
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
            target_direction="left",
            target_eccentricity_deg=-10.0,
            intended_iti_s=ITI_DURATION,
            details="expected_response=right"
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