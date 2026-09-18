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


from event_logger import EventLogger


def main():
    print("=" * 55)
    print("NeuroMirror Experiment 01")
    print("Phase 1C.20A — Trial Metadata Logging Check")
    print("=" * 55)

    experiment_clock = core.Clock()

    logger = EventLogger(
        experiment_clock=experiment_clock
    )

    logger.log_event(
        event_type="experiment_start",
        task="prosaccade"
    )

    logger.log_event(
        event_type="target_onset",
        task="prosaccade",
        trial=1,
        target_direction="right",
        target_eccentricity_deg=10.0,
        intended_iti_s=1.4403,
        details="metadata_test"
    )

    logger.log_event(
        event_type="experiment_end",
        task="prosaccade"
    )

    output_path = (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "development"
        / "event_logger_metadata_test.csv"
    )

    logger.save_csv(output_path)

    target_event = logger.events[1]

    checks = {
        "direction": (
            target_event["target_direction"] == "right"
        ),
        "eccentricity": (
            target_event["target_eccentricity_deg"] == 10.0
        ),
        "iti": (
            target_event["intended_iti_s"] == 1.4403
        ),
    }

    print("\nStored metadata:")
    print(
        "target_direction       :",
        target_event["target_direction"]
    )
    print(
        "target_eccentricity_deg:",
        target_event["target_eccentricity_deg"]
    )
    print(
        "intended_iti_s         :",
        target_event["intended_iti_s"]
    )

    print("\nValidation:")
    print("Direction correct      :", checks["direction"])
    print("Eccentricity correct   :", checks["eccentricity"])
    print("ITI correct            :", checks["iti"])

    print("\nCSV saved:")
    print(output_path)

    print("\n" + "=" * 55)

    if all(checks.values()):
        print("Status : PASS")
    else:
        print("Status : FAIL")


if __name__ == "__main__":
    main()