import sys
from pathlib import Path

import numpy as np
import pytest


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


from movement_detector import (
    detect_candidate_movement_onset,
)


def test_left_movement_detected():

    timestamps = [
        0.90,
        1.00,
        1.03,
        1.06,
        1.09,
    ]

    gaze = [
        0.50,
        0.50,
        0.53,
        0.54,
        0.55,
    ]

    result = detect_candidate_movement_onset(
        timestamps=timestamps,
        gaze_signal=gaze,
        target_onset=1.00,
        baseline_median=0.50,
        baseline_mad=0.005,
        direction="LEFT",
    )

    assert result is not None

    assert np.isclose(
        result["onset_timestamp"],
        1.03,
    )

    assert np.isclose(
        result["onset_relative_ms"],
        30.0,
    )


def test_right_movement_detected():

    timestamps = [
        0.90,
        1.00,
        1.03,
        1.06,
        1.09,
    ]

    gaze = [
        0.50,
        0.50,
        0.47,
        0.46,
        0.45,
    ]

    result = detect_candidate_movement_onset(
        timestamps=timestamps,
        gaze_signal=gaze,
        target_onset=1.00,
        baseline_median=0.50,
        baseline_mad=0.005,
        direction="RIGHT",
    )

    assert result is not None

    assert np.isclose(
        result["onset_timestamp"],
        1.03,
    )


def test_persistence_rejects_isolated_crossing():

    timestamps = [
        1.00,
        1.03,
        1.06,
        1.09,
        1.12,
    ]

    gaze = [
        0.50,
        0.54,
        0.50,
        0.54,
        0.50,
    ]

    result = detect_candidate_movement_onset(
        timestamps=timestamps,
        gaze_signal=gaze,
        target_onset=1.00,
        baseline_median=0.50,
        baseline_mad=0.005,
        direction="LEFT",
    )

    assert result is None


def test_no_movement_returns_none():

    timestamps = [
        1.00,
        1.03,
        1.06,
        1.09,
    ]

    gaze = [
        0.50,
        0.51,
        0.49,
        0.50,
    ]

    result = detect_candidate_movement_onset(
        timestamps=timestamps,
        gaze_signal=gaze,
        target_onset=1.00,
        baseline_median=0.50,
        baseline_mad=0.005,
        direction="LEFT",
    )

    assert result is None


def test_invalid_direction():

    with pytest.raises(ValueError):

        detect_candidate_movement_onset(
            timestamps=[1.00, 1.03],
            gaze_signal=[0.50, 0.51],
            target_onset=1.00,
            baseline_median=0.50,
            baseline_mad=0.005,
            direction="UP",
        )