import random


def has_valid_consecutive_limit(sequence, max_consecutive=3):
    """
    Check that the sequence does not contain more than
    max_consecutive identical directions in a row.
    """

    if not sequence:
        return True

    consecutive_count = 1

    for index in range(1, len(sequence)):

        if sequence[index] == sequence[index - 1]:
            consecutive_count += 1
        else:
            consecutive_count = 1

        if consecutive_count > max_consecutive:
            return False

    return True


def generate_balanced_sequence(
    trials_per_direction=10,
    max_consecutive=3,
    seed=None
):
    """
    Generate a balanced LEFT/RIGHT trial sequence.

    The sequence contains an equal number of left and right
    trials and does not allow more than max_consecutive
    identical directions in a row.
    """

    rng = random.Random(seed)

    base_sequence = (
        ["left"] * trials_per_direction
        + ["right"] * trials_per_direction
    )

    attempts = 0

    while True:
        attempts += 1

        sequence = base_sequence.copy()
        rng.shuffle(sequence)

        if has_valid_consecutive_limit(
            sequence,
            max_consecutive=max_consecutive
        ):
            return sequence, attempts

def generate_random_iti_sequence(
    num_trials,
    min_duration=1.0,
    max_duration=1.5,
    seed=None
):
    """
    Generate a reproducible sequence of randomized
    inter-trial interval (ITI) durations.

    Each ITI duration is sampled uniformly between
    min_duration and max_duration.
    """

    if num_trials <= 0:
        raise ValueError("num_trials must be greater than 0")

    if min_duration > max_duration:
        raise ValueError(
            "min_duration cannot be greater than max_duration"
        )

    rng = random.Random(seed)

    return [
        rng.uniform(min_duration, max_duration)
        for _ in range(num_trials)
    ]