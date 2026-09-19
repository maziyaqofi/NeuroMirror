import numpy as np
import pandas as pd


DEFAULT_BASELINE_WINDOW = 0.300


def extract_baseline_samples(
    gaze_df,
    target_onset,
    window=DEFAULT_BASELINE_WINDOW,
    signal_column="average_iris_ratio",
):
    """
    Extract valid gaze samples immediately preceding target onset.

    Parameters
    ----------
    gaze_df : pandas.DataFrame
        Gaze recording containing timestamp and signal columns.

    target_onset : float
        Software-recorded target onset timestamp in seconds.

    window : float
        Duration of the pre-target baseline window in seconds.

    signal_column : str
        Column containing the gaze signal.

    Returns
    -------
    pandas.Series
        Valid gaze samples within:
        [target_onset - window, target_onset)
    """

    required_columns = {
        "timestamp",
        signal_column,
    }

    missing = (
        required_columns
        - set(gaze_df.columns)
    )

    if missing:
        raise ValueError(
            "Missing required column(s): "
            + ", ".join(sorted(missing))
        )

    if window <= 0:
        raise ValueError(
            "Baseline window must be > 0."
        )

    baseline = gaze_df[
        (
            gaze_df["timestamp"]
            >= target_onset - window
        )
        &
        (
            gaze_df["timestamp"]
            < target_onset
        )
    ][signal_column]

    return baseline.dropna()


def calculate_baseline_median(
    baseline_samples,
):
    """
    Calculate the median of valid baseline samples.

    Returns NaN when no valid samples are available.
    """

    values = np.asarray(
        baseline_samples,
        dtype=float,
    )

    values = values[
        np.isfinite(values)
    ]

    if len(values) == 0:
        return np.nan

    return float(
        np.median(values)
    )