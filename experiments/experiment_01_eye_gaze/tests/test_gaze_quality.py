import sys
from pathlib import Path

import numpy as np


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


from gaze_quality import (
    calculate_baseline_quality,
)


def test_quality_metrics():

    samples = [
        0.49,
        0.50,
        0.51,
    ]

    result = (
        calculate_baseline_quality(
            samples
        )
    )

    assert result[
        "sample_count"
    ] == 3

    assert np.isclose(
        result["median"],
        0.50,
    )

    assert np.isclose(
        result["mad"],
        0.01,
    )

    assert np.isclose(
        result["median_frame_step"],
        0.01,
    )

    assert np.isclose(
        result["p90_frame_step"],
        0.01,
    )


def test_nan_samples_are_removed():

    samples = [
        0.49,
        np.nan,
        0.51,
    ]

    result = (
        calculate_baseline_quality(
            samples
        )
    )

    assert result[
        "sample_count"
    ] == 2

    assert np.isclose(
        result["median"],
        0.50,
    )


def test_single_sample():

    result = (
        calculate_baseline_quality(
            [0.50]
        )
    )

    assert result[
        "sample_count"
    ] == 1

    assert result[
        "median"
    ] == 0.50

    assert result[
        "mad"
    ] == 0.0

    assert np.isnan(
        result[
            "median_frame_step"
        ]
    )

    assert np.isnan(
        result[
            "p90_frame_step"
        ]
    )


def test_empty_baseline():

    result = (
        calculate_baseline_quality(
            []
        )
    )

    assert result[
        "sample_count"
    ] == 0

    assert np.isnan(
        result["median"]
    )

    assert np.isnan(
        result["mad"]
    )

    assert np.isnan(
        result[
            "median_frame_step"
        ]
    )


def test_frame_step_behavior():

    samples = [
        0.50,
        0.51,
        0.50,
        0.51,
    ]

    result = (
        calculate_baseline_quality(
            samples
        )
    )

    assert np.isclose(
        result[
            "median_frame_step"
        ],
        0.01,
    )

    assert np.isclose(
        result[
            "p90_frame_step"
        ],
        0.01,
    )