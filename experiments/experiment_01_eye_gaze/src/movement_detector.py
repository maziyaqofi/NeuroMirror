import numpy as np


DEFAULT_THRESHOLD_MULTIPLIER = 6.0
DEFAULT_PERSISTENCE = 3


DIRECTION_SIGN = {
    "LEFT": 1,
    "RIGHT": -1,
}


def detect_candidate_movement_onset(
    timestamps,
    gaze_signal,
    target_onset,
    baseline_median,
    baseline_mad,
    direction,
    threshold_multiplier=DEFAULT_THRESHOLD_MULTIPLIER,
    persistence=DEFAULT_PERSISTENCE,
):
    """
    Detect candidate gaze movement onset using the frozen
    development detector v0.1.

    Parameters
    ----------
    timestamps : array-like
        Sample timestamps in seconds.

    gaze_signal : array-like
        Gaze signal values corresponding to timestamps.

    target_onset : float
        Software-recorded target onset timestamp.

    baseline_median : float
        Median gaze value from the pre-target baseline.

    baseline_mad : float
        Median absolute deviation of the pre-target baseline.

    direction : str
        Expected movement direction: "LEFT" or "RIGHT".

    threshold_multiplier : float
        MAD multiplier used for movement detection.
        Detector v0.1 uses 6.

    persistence : int
        Number of consecutive threshold-crossing samples
        required. Detector v0.1 uses 3.

    Returns
    -------
    dict or None
        Detection information, or None when no sustained
        movement is detected.

    Notes
    -----
    The returned onset is a candidate gaze movement onset
    relative to software-recorded target onset.

    It must not be interpreted as clinical saccadic latency.
    """

    direction = direction.upper()

    if direction not in DIRECTION_SIGN:
        raise ValueError(
            "direction must be 'LEFT' or 'RIGHT'."
        )

    if persistence < 1:
        raise ValueError(
            "persistence must be >= 1."
        )

    timestamps = np.asarray(
        timestamps,
        dtype=float,
    )

    gaze_signal = np.asarray(
        gaze_signal,
        dtype=float,
    )

    if len(timestamps) != len(gaze_signal):
        raise ValueError(
            "timestamps and gaze_signal must have equal length."
        )

    if not np.isfinite(baseline_median):
        return None

    if not np.isfinite(baseline_mad):
        return None

    direction_sign = DIRECTION_SIGN[
        direction
    ]

    threshold = (
        threshold_multiplier
        * baseline_mad
    )

    consecutive = 0

    for index, (timestamp, gaze_value) in enumerate(
        zip(timestamps, gaze_signal)
    ):

        if timestamp < target_onset:
            continue

        if not np.isfinite(gaze_value):
            consecutive = 0
            continue

        displacement = (
            gaze_value
            - baseline_median
        )

        directed_displacement = (
            displacement
            * direction_sign
        )

        if directed_displacement >= threshold:

            consecutive += 1

            if consecutive >= persistence:

                onset_index = (
                    index
                    - persistence
                    + 1
                )

                onset_timestamp = float(
                    timestamps[
                        onset_index
                    ]
                )

                onset_relative_seconds = (
                    onset_timestamp
                    - target_onset
                )

                return {
                    "onset_timestamp":
                        onset_timestamp,

                    "onset_relative_seconds":
                        float(
                            onset_relative_seconds
                        ),

                    "onset_relative_ms":
                        float(
                            onset_relative_seconds
                            * 1000.0
                        ),

                    "direction":
                        direction,

                    "direction_sign":
                        direction_sign,

                    "threshold":
                        float(threshold),

                    "threshold_multiplier":
                        float(
                            threshold_multiplier
                        ),

                    "persistence":
                        int(persistence),
                }

        else:
            consecutive = 0

    return None
