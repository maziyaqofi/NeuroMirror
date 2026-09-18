import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

SRC_DIR = (
    PROJECT_ROOT
    / "experiments"
    / "experiment_01_eye_gaze"
    / "src"
)

sys.path.insert(0, str(SRC_DIR))


from randomization import (
    generate_balanced_sequence,
    has_valid_consecutive_limit
)


TEST_SEED = 20260918


def main():
    print("=" * 50)
    print("NeuroMirror Experiment 01")
    print("Phase 1C — Prosaccade Randomization Check")
    print("=" * 50)

    sequence, attempts = generate_balanced_sequence(
        trials_per_direction=10,
        max_consecutive=3,
        seed=TEST_SEED
    )

    left_count = sequence.count("left")
    right_count = sequence.count("right")

    valid_consecutive = has_valid_consecutive_limit(
        sequence,
        max_consecutive=3
    )

    print(f"\nRandom seed       : {TEST_SEED}")
    print(f"Generation attempts: {attempts}")
    print(f"Total trials      : {len(sequence)}")
    print(f"LEFT trials       : {left_count}")
    print(f"RIGHT trials      : {right_count}")
    print(f"Consecutive valid : {valid_consecutive}")

    print("\nGenerated sequence:")
    print("-" * 35)

    for trial_number, direction in enumerate(
        sequence,
        start=1
    ):
        print(
            f"Trial {trial_number:02d} : "
            f"{direction.upper()}"
        )

    print("-" * 35)

    all_checks_passed = (
        len(sequence) == 20
        and left_count == 10
        and right_count == 10
        and valid_consecutive
    )

    if all_checks_passed:
        print("\nStatus : PASS")
    else:
        print("\nStatus : FAIL")


if __name__ == "__main__":
    main()
    