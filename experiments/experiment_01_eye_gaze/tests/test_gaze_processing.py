import sys
from pathlib import Path

import numpy as np
import pandas as pd


SRC_DIR = (
    Path(__file__)
    .resolve()
    .parents[1]
    / "src"
)

sys.path.insert(
    0,
    str(SRC_DIR)
)


from gaze_processing import (
    extract_baseline_samples,
    calculate_baseline_median,
)


def test_extract_baseline_samples():

    gaze = pd.DataFrame({
        "timestamp": [
            0.60,
            0.70,
            0.80,
            0.90,
            1.00,
        ],
        "average_iris_ratio": [
            0.48,
            0.49,
            0.50,
            0.51,
            0.70,
        ],
    })

    baseline = extract_baseline_samples(
        gaze_df=gaze,
        target_onset=1.00,
        window=0.300,
    )

    assert len(baseline) == 3

    assert np.allclose(
        baseline.to_numpy(),
        [
            0.49,
            0.50,
            0.51,
        ],
    )


def test_target_onset_not_in_baseline():

    gaze = pd.DataFrame({
        "timestamp": [
            0.90,
            1.00,
        ],
        "average_iris_ratio": [
            0.50,
            0.90,
        ],
    })

    baseline = extract_baseline_samples(
        gaze_df=gaze,
        target_onset=1.00,
        window=0.300,
    )

    assert len(baseline) == 1

    assert baseline.iloc[0] == 0.50


def test_nan_samples_are_removed():

    gaze = pd.DataFrame({
        "timestamp": [
            0.80,
            0.90,
        ],
        "average_iris_ratio": [
            np.nan,
            0.50,
        ],
    })

    baseline = extract_baseline_samples(
        gaze_df=gaze,
        target_onset=1.00,
    )

    assert len(baseline) == 1


def test_baseline_median():

    samples = pd.Series([
        0.49,
        0.50,
        0.51,
    ])

    median = calculate_baseline_median(
        samples
    )

    assert median == 0.50


def test_empty_baseline_returns_nan():

    median = calculate_baseline_median(
        []
    )

    assert np.isnan(median)