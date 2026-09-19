import numpy as np


def calculate_baseline_quality(
    baseline_samples,
):
    """
    Calculate descriptive quality metrics for a
    pre-target gaze baseline.

    This function characterizes baseline quality only.
    It does NOT classify a baseline as PASS or FAIL.

    Parameters
    ----------
    baseline_samples : array-like
        Gaze signal samples from the local pre-target
        baseline window.

    Returns
    -------
    dict
        Baseline quality metrics.
    """

    values = np.asarray(
        baseline_samples,
        dtype=float,
    )

    values = values[
        np.isfinite(values)
    ]

    sample_count = len(values)

    if sample_count == 0:
        return {
            "sample_count": 0,
            "median": np.nan,
            "mad": np.nan,
            "median_frame_step": np.nan,
            "p90_frame_step": np.nan,
        }

    median = float(
        np.median(values)
    )

    mad = float(
        np.median(
            np.abs(
                values - median
            )
        )
    )

    if sample_count >= 2:

        frame_steps = np.abs(
            np.diff(values)
        )

        median_frame_step = float(
            np.median(
                frame_steps
            )
        )

        p90_frame_step = float(
            np.percentile(
                frame_steps,
                90,
            )
        )

    else:

        median_frame_step = np.nan
        p90_frame_step = np.nan

    return {
        "sample_count": sample_count,
        "median": median,
        "mad": mad,
        "median_frame_step":
            median_frame_step,
        "p90_frame_step":
            p90_frame_step,
    }