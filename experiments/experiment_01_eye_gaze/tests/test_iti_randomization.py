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


from randomization import generate_random_iti_sequence


TEST_SEED = 20260918
NUM_TRIALS = 20
MIN_ITI = 1.0
MAX_ITI = 1.5


def main():
    print("=" * 50)
    print("NeuroMirror Experiment 01")
    print("Phase 1C — Randomized ITI Validation")
    print("=" * 50)

    sequence_a = generate_random_iti_sequence(
        num_trials=NUM_TRIALS,
        min_duration=MIN_ITI,
        max_duration=MAX_ITI,
        seed=TEST_SEED
    )

    sequence_b = generate_random_iti_sequence(
        num_trials=NUM_TRIALS,
        min_duration=MIN_ITI,
        max_duration=MAX_ITI,
        seed=TEST_SEED
    )

    # Reproducibility
    reproducible = sequence_a == sequence_b

    # Range validation
    all_in_range = all(
        MIN_ITI <= duration <= MAX_ITI
        for duration in sequence_a
    )

    # Length validation
    correct_length = len(sequence_a) == NUM_TRIALS

    print(f"\nRandom seed       : {TEST_SEED}")
    print(f"Number of ITIs    : {len(sequence_a)}")
    print(
        f"Allowed range     : "
        f"{MIN_ITI:.2f}–{MAX_ITI:.2f} s"
    )

    print("\nGenerated ITI sequence:")
    print("-" * 35)

    for trial_number, duration in enumerate(
        sequence_a,
        start=1
    ):
        print(
            f"Trial {trial_number:02d} : "
            f"{duration:.4f} s"
        )

    print("-" * 35)

    print("\nValidation:")
    print(f"Correct length    : {correct_length}")
    print(f"All ITIs in range : {all_in_range}")
    print(f"Reproducible      : {reproducible}")

    print(
        f"Minimum generated : "
        f"{min(sequence_a):.4f} s"
    )

    print(
        f"Maximum generated : "
        f"{max(sequence_a):.4f} s"
    )

    all_checks_passed = (
        correct_length
        and all_in_range
        and reproducible
    )

    print("\n" + "=" * 50)

    if all_checks_passed:
        print("Status : PASS")
    else:
        print("Status : FAIL")


if __name__ == "__main__":
    main()