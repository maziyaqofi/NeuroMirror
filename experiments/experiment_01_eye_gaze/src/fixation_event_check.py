from pathlib import Path

from psychopy import visual, monitors, core, event

from event_logger import EventLogger, generate_log_filename


MONITOR_NAME = "neuromirror_macbook"

FIXATION_DURATION = 10.0
REST_DURATION = 3.0
TOTAL_BLOCKS = 3


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def escape_pressed():
    return "escape" in event.getKeys()


def run_fixation(
    win,
    fixation,
    logger,
    block_number
):
    fixation.draw()
    win.flip()

    logger.log_event(
        event_type="fixation_onset",
        task="fixation",
        block=block_number
    )

    timer = core.Clock()

    while timer.getTime() < FIXATION_DURATION:

        if escape_pressed():
            return True

        fixation.draw()
        win.flip()

    logger.log_event(
        event_type="fixation_offset",
        task="fixation",
        block=block_number
    )

    return False


def run_rest(
    win,
    rest_text,
    logger,
    block_number
):
    rest_text.draw()
    win.flip()

    logger.log_event(
        event_type="rest_onset",
        task="fixation",
        block=block_number
    )

    timer = core.Clock()

    while timer.getTime() < REST_DURATION:

        if escape_pressed():
            return True

        rest_text.draw()
        win.flip()

    logger.log_event(
        event_type="rest_offset",
        task="fixation",
        block=block_number
    )

    return False


def main():
    print("=" * 50)
    print("NeuroMirror Experiment 01")
    print("Phase 1C — Fixation Event Integration")
    print("=" * 50)

    monitor = monitors.Monitor(
        MONITOR_NAME
    )

    win = visual.Window(
        size=(800, 600),
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

    # One clock for the entire experiment.
    experiment_clock = core.Clock()

    logger = EventLogger(
        experiment_clock=experiment_clock
    )

    logger.log_event(
        event_type="experiment_start"
    )

    aborted = False

    print(f"\nFixation blocks : {TOTAL_BLOCKS}")
    print(
        f"Duration        : "
        f"{FIXATION_DURATION:.1f} s"
    )
    print(
        f"Rest            : "
        f"{REST_DURATION:.1f} s"
    )

    for block in range(
        1,
        TOTAL_BLOCKS + 1
    ):

        print(
            f"\nStarting fixation "
            f"block {block}..."
        )

        aborted = run_fixation(
            win,
            fixation,
            logger,
            block
        )

        if aborted:
            logger.log_event(
                event_type="experiment_abort",
                details="escape_pressed"
            )
            break

        if block < TOTAL_BLOCKS:

            aborted = run_rest(
                win,
                rest_text,
                logger,
                block
            )

            if aborted:
                logger.log_event(
                    event_type="experiment_abort",
                    details="escape_pressed"
                )
                break

    if not aborted:
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

    logger.save_csv(
        output_path
    )

    print("\n" + "=" * 50)

    if aborted:
        print("Status : ABORTED BY USER")
    else:
        print("Status : COMPLETED")

    print(
        f"Total events : "
        f"{len(logger.events)}"
    )


if __name__ == "__main__":
    main()