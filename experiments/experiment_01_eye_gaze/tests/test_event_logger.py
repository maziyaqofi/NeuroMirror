import sys
from pathlib import Path

from psychopy import core


PROJECT_ROOT = Path(__file__).resolve().parents[3]

SRC_DIR = (
    PROJECT_ROOT
    / "experiments"
    / "experiment_01_eye_gaze"
    / "src"
)

sys.path.insert(0, str(SRC_DIR))


from event_logger import (
    EventLogger,
    generate_log_filename
)


def main():
    print("=" * 50)
    print("NeuroMirror Experiment 01")
    print("Phase 1C — Event Logger Check")
    print("=" * 50)

    experiment_clock = core.Clock()

    logger = EventLogger(
        experiment_clock=experiment_clock
    )

    print("\nExperiment clock started.")

    logger.log_event(
        event_type="experiment_start"
    )

    core.wait(1.0)

    logger.log_event(
        event_type="fixation_onset",
        task="fixation",
        block=1
    )

    core.wait(2.0)

    logger.log_event(
        event_type="fixation_offset",
        task="fixation",
        block=1
    )

    core.wait(1.0)

    logger.log_event(
        event_type="experiment_end"
    )

    filename = generate_log_filename()

    output_path = (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "development"
        / filename
    )

    logger.save_csv(output_path)

    print("\nTotal events:", len(logger.events))
    print("Status      : COMPLETED")


if __name__ == "__main__":
    main()