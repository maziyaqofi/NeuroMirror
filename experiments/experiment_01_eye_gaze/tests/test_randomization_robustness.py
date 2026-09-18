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


REPRODUCIBILITY_SEED = 20260918
TOTAL_TEST_SEEDS = 100


def validate_sequence(sequence):
    return (
        len(sequence) == 20
        and sequence.count("left") == 10
        and sequence.count("right") == 10
        and has_valid_consecutive_limit(
            sequence,
            max_consecutive=3
        )
    )


def main():
    print("=" * 50)
    print("NeuroMirror Experiment 01")
    print("Phase 1C — Randomization Robustness Check")
    print("=" * 50)

    # -----------------------------------------
    # Reproducibility test
    # -----------------------------------------

    sequence_a, _ = generate_balanced_sequence(
        trials_per_direction=10,
        max_consecutive=3,
        seed=REPRODUCIBILITY_SEED
    )

    sequence_b, _ = generate_balanced_sequence(
        trials_per_direction=10,
        max_consecutive=3,
        seed=REPRODUCIBILITY_SEED
    )

    reproducible = sequence_a == sequence_b

    print("\nReproducibility test")
    print("-" * 30)
    print(
        f"Seed              : "
        f"{REPRODUCIBILITY_SEED}"
    )
    print(
        f"Sequences match   : "
        f"{reproducible}"
    )

    # -----------------------------------------
    # Multi-seed test
    # -----------------------------------------

    failures = []
    maximum_attempts = 0

    for seed in range(TOTAL_TEST_SEEDS):

        sequence, attempts = generate_balanced_sequence(
            trials_per_direction=10,
            max_consecutive=3,
            seed=seed
        )

        maximum_attempts = max(
            maximum_attempts,
            attempts
        )

        if not validate_sequence(sequence):
            failures.append(seed)

    print("\nMulti-seed test")
    print("-" * 30)
    print(
        f"Seeds tested       : "
        f"{TOTAL_TEST_SEEDS}"
    )
    print(
        f"Failed seeds       : "
        f"{len(failures)}"
    )
    print(
        f"Maximum attempts   : "
        f"{maximum_attempts}"
    )

    all_passed = (
        reproducible
        and len(failures) == 0
    )

    print("\n" + "=" * 50)

    if all_passed:
        print("Status : PASS")
    else:
        print("Status : FAIL")

        if failures:
            print(
                "Failed seed values:",
                failures
            )


if __name__ == "__main__":
    main()