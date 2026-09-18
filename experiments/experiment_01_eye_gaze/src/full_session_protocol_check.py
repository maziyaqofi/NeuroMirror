from psychopy import visual, core, event

from event_logger import EventLogger, generate_log_filename

from randomization import (
    generate_balanced_sequence,
    generate_random_iti_sequence
)

PROSACCADE_FIXATION_DURATION = 1.0
PROSACCADE_TARGET_DURATION = 1.0
PROSACCADE_MIN_ITI = 1.0
PROSACCADE_MAX_ITI = 1.5

ANTISACCADE_FIXATION_DURATION = 1.0
ANTISACCADE_TARGET_DURATION = 1.0
ANTISACCADE_MIN_ITI = 1.0
ANTISACCADE_MAX_ITI = 1.5

TARGET_ECCENTRICITY = 10.0
TEST_SEED = 20260918

WINDOW_SIZE = (1200, 750)
FIXATION_DURATION = 10.0
REST_DURATION = 3.0
TOTAL_FIXATION_BLOCKS = 3


def wait_for_space_or_escape(win, message):
    """Display a message and wait for SPACE or ESC."""

    text = visual.TextStim(
        win,
        text=message,
        color="black",
        height=0.6,
        units="deg",
        wrapWidth=25
    )

    text.draw()
    win.flip()

    keys = event.waitKeys(
        keyList=["space", "escape"]
    )

    if "escape" in keys:
        return True

    return False

def run_fixation_block(
    win,
    fixation,
    logger,
    block_number
):
    fixation.draw()

    win.callOnFlip(
        logger.log_event,
        event_type="fixation_onset",
        task="fixation",
        block=block_number,
        details="center"
    )

    win.flip()

    timer = core.Clock()

    while timer.getTime() < FIXATION_DURATION:
        if "escape" in event.getKeys():
            logger.log_event(
                event_type="experiment_abort",
                task="fixation",
                block=block_number,
                details="escape_pressed"
            )
            return None, True

        fixation.draw()
        win.flip()

    duration = timer.getTime()

    win.callOnFlip(
        logger.log_event,
        event_type="fixation_offset",
        task="fixation",
        block=block_number,
        details="center"
    )

    win.flip()

    return duration, False


def run_fixation_rest(
    win,
    rest_text,
    logger,
    block_number
):
    rest_text.draw()

    win.callOnFlip(
        logger.log_event,
        event_type="rest_onset",
        task="fixation",
        block=block_number
    )

    win.flip()

    timer = core.Clock()

    while timer.getTime() < REST_DURATION:
        if "escape" in event.getKeys():
            logger.log_event(
                event_type="experiment_abort",
                task="fixation",
                block=block_number,
                details="escape_pressed"
            )
            return True

        rest_text.draw()
        win.flip()

    win.callOnFlip(
        logger.log_event,
        event_type="rest_offset",
        task="fixation",
        block=block_number
    )

    win.flip()

    return False

def hold_prosaccade_stimulus(win, stimulus, duration):
    timer = core.Clock()

    while timer.getTime() < duration:
        if "escape" in event.getKeys():
            return True

        stimulus.draw()
        win.flip()

    return False


def hold_prosaccade_blank(win, duration):
    timer = core.Clock()

    while timer.getTime() < duration:
        if "escape" in event.getKeys():
            return True

        win.flip()

    return False

# Trial Functions
def run_prosaccade_trial(
    win,
    fixation,
    left_target,
    right_target,
    logger,
    trial_number,
    direction,
    iti_duration
):
    # Central fixation
    fixation.draw()

    win.callOnFlip(
        logger.log_event,
        event_type="fixation_onset",
        task="prosaccade",
        trial=trial_number,
        details="center"
    )

    win.flip()

    aborted = hold_prosaccade_stimulus(
        win,
        fixation,
        PROSACCADE_FIXATION_DURATION
    )

    if aborted:
        return True

    # Peripheral target
    if direction == "right":
        target = right_target
        target_details = "right_10deg"
        target_eccentricity = TARGET_ECCENTRICITY
    else:
        target = left_target
        target_details = "left_10deg"
        target_eccentricity = -TARGET_ECCENTRICITY

    target.draw()

    win.callOnFlip(
        logger.log_event,
        event_type="target_onset",
        task="prosaccade",
        trial=trial_number,
        target_direction=direction,
        target_eccentricity_deg=target_eccentricity,
        intended_iti_s=iti_duration,
        details=target_details
    )

    win.flip()

    aborted = hold_prosaccade_stimulus(
        win,
        target,
        PROSACCADE_TARGET_DURATION
    )

    if aborted:
        return True

    # Target offset + ITI onset
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

    win.flip()

    aborted = hold_prosaccade_blank(
        win,
        iti_duration
    )

    if aborted:
        return True

    # ITI offset
    win.callOnFlip(
        logger.log_event,
        event_type="iti_offset",
        task="prosaccade",
        trial=trial_number
    )

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
            "target_eccentricity_deg": TARGET_ECCENTRICITY,
            "expected_response_direction": "left",
        }

    elif direction == "left":
        return {
            "target": left_target,
            "target_direction": "left",
            "target_eccentricity_deg": -TARGET_ECCENTRICITY,
            "expected_response_direction": "right",
        }

    else:
        raise ValueError(
            f"Invalid direction: {direction}"
        )

def run_antisaccade_trial(
    win,
    fixation,
    left_target,
    right_target,
    logger,
    trial_number,
    direction,
    iti_duration
):
    # Central fixation
    fixation.draw()

    win.callOnFlip(
        logger.log_event,
        event_type="fixation_onset",
        task="antisaccade",
        trial=trial_number,
        details="center"
    )

    win.flip()

    aborted = hold_prosaccade_stimulus(
        win,
        fixation,
        ANTISACCADE_FIXATION_DURATION
    )

    if aborted:
        return True

    # Determine target and expected opposite response
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

    # Target onset
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

    aborted = hold_prosaccade_stimulus(
        win,
        target,
        ANTISACCADE_TARGET_DURATION
    )

    if aborted:
        return True

    # Target offset + ITI onset
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

    aborted = hold_prosaccade_blank(
        win,
        iti_duration
    )

    if aborted:
        return True

    # ITI offset
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

    print("=" * 60)
    print("NeuroMirror Experiment 01")
    print("Phase 1C.26 — Full Session Protocol Integration")
    print("=" * 60)

    # --------------------------------------------------
    # WINDOW
    # --------------------------------------------------

    win = visual.Window(
        size=WINDOW_SIZE,
        fullscr=False,
        monitor="neuromirror_macbook",
        units="deg",
        color="white"
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
    
    # --------------------------------------------------
    # SHARED SESSION CLOCK + LOGGER
    # --------------------------------------------------

    session_clock = core.Clock()

    logger = EventLogger(
        experiment_clock=session_clock
    )

    # --------------------------------------------------
    # SESSION START SCREEN
    # --------------------------------------------------

    aborted = wait_for_space_or_escape(
        win,
        (
            "NeuroMirror Experiment 01\n\n"
            "Full Session Development Test\n\n"
            "Press SPACE to begin."
        )
    )

    if aborted:
        win.close()
        core.quit()

    logger.log_event(
        event_type="session_start",
        task="session",
        details="full_session_protocol"
    )

    # --------------------------------------------------
    # FIXATION PLACEHOLDER
    # --------------------------------------------------

    print("\n[1/3] Fixation block")

    aborted = wait_for_space_or_escape(
        win,
        (
            "Part 1 — Fixation\n\n"
            "Keep looking at the center of the screen.\n\n"
            "Press SPACE to continue."
        )
    )

    if aborted:
        win.close()
        core.quit()

    print(
        f"Running {TOTAL_FIXATION_BLOCKS} fixation blocks "
        f"× {FIXATION_DURATION:.1f} s"
    )

    for block_number in range(
        1,
        TOTAL_FIXATION_BLOCKS + 1
    ):
        print(
            f"\nStarting fixation block "
            f"{block_number}..."
        )

        duration, aborted = run_fixation_block(
            win=win,
            fixation=fixation,
            logger=logger,
            block_number=block_number
        )

        if aborted:
            break

        print(
            f"Fixation block {block_number} completed "
            f"({duration:.4f} s)"
        )

        if block_number < TOTAL_FIXATION_BLOCKS:
            print("Rest...")

            aborted = run_fixation_rest(
                win=win,
                rest_text=rest_text,
                logger=logger,
                block_number=block_number
            )

            if aborted:
                break

    # --------------------------------------------------
    # PROSACCADE PLACEHOLDER
    # --------------------------------------------------

    print("[2/3] Prosaccade block")

    aborted = wait_for_space_or_escape(
        win,
        (
            "Part 2 — Prosaccade\n\n"
            "Look at the dot as quickly as you can "
            "when it appears.\n\n"
            "Press SPACE to continue."
        )
    )

    if aborted:
        win.close()
        core.quit()

    trial_sequence, generation_attempts = generate_balanced_sequence(
        trials_per_direction=10,
        max_consecutive=3,
        seed=TEST_SEED
    )

    iti_sequence = generate_random_iti_sequence(
        num_trials=20,
        min_duration=PROSACCADE_MIN_ITI,
        max_duration=PROSACCADE_MAX_ITI,
        seed=TEST_SEED
    )

    print(f"\nProsaccade random seed: {TEST_SEED}")
    print(f"Generation attempts   : {generation_attempts}")

    for trial_number, (direction, iti_duration) in enumerate(
        zip(trial_sequence, iti_sequence),
        start=1
    ):
        print(
            f"\nProsaccade trial {trial_number:02d} | "
            f"{direction.upper()} | "
            f"ITI={iti_duration:.4f}s"
        )

        aborted = run_prosaccade_trial(
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
                task="prosaccade",
                trial=trial_number,
                details="escape_pressed"
            )
            break

        if aborted:
            logger.save_csv(generate_log_filename())
            win.close()
            core.quit()

    # --------------------------------------------------
    # ANTISACCADE PLACEHOLDER
    # --------------------------------------------------

    print("[3/3] Antisaccade block")

    aborted = wait_for_space_or_escape(
        win,
        (
            "Part 3 — Antisaccade\n\n"
            "When a dot appears on one side,\n"
            "look in the OPPOSITE direction.\n\n"
            "Press SPACE to continue."
        )
    )

    if aborted:
        win.close()
        core.quit()

    antisaccade_sequence, antisaccade_attempts = (
        generate_balanced_sequence(
            trials_per_direction=10,
            max_consecutive=3,
            seed=TEST_SEED
        )
    )

    antisaccade_iti_sequence = generate_random_iti_sequence(
        num_trials=20,
        min_duration=ANTISACCADE_MIN_ITI,
        max_duration=ANTISACCADE_MAX_ITI,
        seed=TEST_SEED
    )

    print(f"\nAntisaccade random seed: {TEST_SEED}")
    print(
        f"Generation attempts    : "
        f"{antisaccade_attempts}"
    )

    for trial_number, (direction, iti_duration) in enumerate(
        zip(
            antisaccade_sequence,
            antisaccade_iti_sequence
        ),
        start=1
    ):
        expected_response = (
            "LEFT"
            if direction == "right"
            else "RIGHT"
        )

        print(
            f"\nAntisaccade trial {trial_number:02d} | "
            f"Target={direction.upper()} | "
            f"Expected={expected_response} | "
            f"ITI={iti_duration:.4f}s"
        )

        aborted = run_antisaccade_trial(
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

    # --------------------------------------------------
    # SESSION END
    # --------------------------------------------------

    logger.log_event(
        event_type="session_end",
        task="session",
        details="full_session_protocol"
    )

    output_path = generate_log_filename()

    logger.save_csv(output_path)

    print("\n" + "=" * 60)
    print("Status: COMPLETED")
    print("Full session skeleton completed.")
    print("=" * 60)

    wait_for_space_or_escape(
        win,
        (
            "Development session completed.\n\n"
            "Press SPACE to close."
        )
    )

    win.close()
    core.quit()


if __name__ == "__main__":
    main()