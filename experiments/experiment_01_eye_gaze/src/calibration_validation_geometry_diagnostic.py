"""
NeuroMirror Phase 1F.3C
Calibration–Validation Geometry Diagnostic

Purpose
-------
Investigate differences in raw eye-geometry features between
the 9-point calibration run and the independent validation run.

This diagnostic does not refit, tune, or modify the
calibration model.

Its purpose is to characterize possible geometry shifts
associated with the observed validation error.
"""

from pathlib import Path
import csv
import statistics
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

DATA_DIR = Path(
    "data/raw/development"
)

CALIBRATION_GAZE_FILE = DATA_DIR / (
    "calibration_9point_gaze_"
    "20260920_064846.csv"
)

CALIBRATION_EVENT_FILE = DATA_DIR / (
    "calibration_9point_events_"
    "20260920_064846.csv"
)

VALIDATION_GAZE_FILE = DATA_DIR / (
    "calibration_validation_gaze_"
    "20260920_100932.csv"
)

VALIDATION_EVENT_FILE = DATA_DIR / (
    "calibration_validation_events_"
    "20260920_100932.csv"
)

TARGET_DURATION = 2.0
STABLE_WINDOW_START = 0.300

FEATURE_NAMES = [
    "left_horizontal_ratio",
    "right_horizontal_ratio",
    "left_vertical_ratio",
    "right_vertical_ratio",
]

CALIBRATION_COEFFICIENTS = np.asarray(
    [
        [89.92139056, 8.63837003],
        [-51.89678705, -283.53476071],
        [-130.50000921, 342.85243975],
        [8.78143847, 39.92118866],
        [-12.50039449, -62.64602084],
    ],
    dtype=float,
)


# ============================================================
# DATA LOADING
# ============================================================

def load_gaze_data(path):

    samples = []

    with path.open(
        "r",
        newline="",
    ) as file:

        reader = csv.DictReader(
            file
        )

        for row in reader:

            samples.append({
                "timestamp":
                    float(row["timestamp"]),

                "frame_number":
                    int(row["frame_number"]),

                "face_detected":
                    int(row["face_detected"]),

                "left_horizontal_ratio":
                    float(row["left_horizontal_ratio"])
                    if row["left_horizontal_ratio"]
                    else None,

                "right_horizontal_ratio":
                    float(row["right_horizontal_ratio"])
                    if row["right_horizontal_ratio"]
                    else None,

                "left_vertical_ratio":
                    float(row["left_vertical_ratio"])
                    if row["left_vertical_ratio"]
                    else None,

                "right_vertical_ratio":
                    float(row["right_vertical_ratio"])
                    if row["right_vertical_ratio"]
                    else None,

                "left_eye_aperture":
                    float(row["left_eye_aperture"])
                    if row["left_eye_aperture"]
                    else None,

                "right_eye_aperture":
                    float(row["right_eye_aperture"])
                    if row["right_eye_aperture"]
                    else None,
            })

    return samples


def load_event_data(path):

    events = []

    with path.open(
        "r",
        newline="",
    ) as file:

        reader = csv.DictReader(
            file
        )

        for row in reader:

            events.append({
                "timestamp":
                    float(row["timestamp"]),

                "point_name":
                    row["point_name"],

                "target_x_deg":
                    float(row["target_x_deg"]),

                "target_y_deg":
                    float(row["target_y_deg"]),
            })

    return events

# ============================================================
# STABLE OBSERVATION EXTRACTION
# ============================================================

def build_stable_observations(
    gaze_samples,
    events,
):
    """
    Build one robust geometry observation per target.

    Uses the same provisional stable-window definition
    for both calibration and validation:

        target onset + 300 ms
        ->
        end of target interval

    Raw samples are not modified or rejected based on
    eye aperture.
    """

    observations = []

    for index, event in enumerate(events):

        start_time = (
            event["timestamp"]
            + STABLE_WINDOW_START
        )

        if index < len(events) - 1:

            end_time = (
                events[index + 1]["timestamp"]
            )

        else:

            end_time = (
                event["timestamp"]
                + TARGET_DURATION
            )

        stable_samples = [
            sample
            for sample in gaze_samples
            if sample["timestamp"] >= start_time
            and sample["timestamp"] < end_time
            and sample["face_detected"] == 1
        ]

        feature_values = {}

        for feature_name in FEATURE_NAMES:

            values = [
                sample[feature_name]
                for sample in stable_samples
                if sample[feature_name] is not None
            ]

            feature_values[feature_name] = (
                statistics.median(values)
                if values
                else None
            )

        aperture_values = {}

        for aperture_name in [
            "left_eye_aperture",
            "right_eye_aperture",
        ]:

            values = [
                sample[aperture_name]
                for sample in stable_samples
                if sample[aperture_name] is not None
            ]

            aperture_values[aperture_name] = (
                statistics.median(values)
                if values
                else None
            )

        observations.append({
            "point_name":
                event["point_name"],

            "target_x_deg":
                event["target_x_deg"],

            "target_y_deg":
                event["target_y_deg"],

            "sample_count":
                len(stable_samples),

            **feature_values,
            **aperture_values,
        })

    return observations

# ============================================================
# CALIBRATION GEOMETRY INTERPOLATION
# ============================================================

def bilinear_interpolate_feature(
    calibration_observations,
    target_x,
    target_y,
    feature_name,
):
    """
    Estimate the expected feature value at an interior
    validation position using bilinear interpolation of
    the surrounding calibration grid points.

    This is a geometry diagnostic only.
    It does not modify or refit the calibration model.
    """

    x_values = sorted({
        observation["target_x_deg"]
        for observation in calibration_observations
    })

    y_values = sorted({
        observation["target_y_deg"]
        for observation in calibration_observations
    })

    x_low = max(
        x for x in x_values
        if x <= target_x
    )

    x_high = min(
        x for x in x_values
        if x >= target_x
    )

    y_low = max(
        y for y in y_values
        if y <= target_y
    )

    y_high = min(
        y for y in y_values
        if y >= target_y
    )

    def get_feature(x, y):

        for observation in calibration_observations:

            if (
                observation["target_x_deg"] == x
                and observation["target_y_deg"] == y
            ):
                return observation[feature_name]

        raise ValueError(
            f"Calibration point not found: "
            f"X={x}, Y={y}"
        )

    q11 = get_feature(
        x_low,
        y_low,
    )

    q21 = get_feature(
        x_high,
        y_low,
    )

    q12 = get_feature(
        x_low,
        y_high,
    )

    q22 = get_feature(
        x_high,
        y_high,
    )

    if x_high == x_low:
        tx = 0.0
    else:
        tx = (
            (target_x - x_low)
            / (x_high - x_low)
        )

    if y_high == y_low:
        ty = 0.0
    else:
        ty = (
            (target_y - y_low)
            / (y_high - y_low)
        )

    interpolated = (
        q11 * (1 - tx) * (1 - ty)
        + q21 * tx * (1 - ty)
        + q12 * (1 - tx) * ty
        + q22 * tx * ty
    )

    return interpolated

# ============================================================
# VALIDATION GEOMETRY COMPARISON
# ============================================================

def compare_validation_geometry(
    calibration_observations,
    validation_observations,
):
    """
    Compare actual validation geometry with geometry expected
    from bilinear interpolation of the calibration grid.

    Delta is defined as:

        actual validation feature
        -
        expected calibration feature

    This is diagnostic only.
    """

    comparisons = []

    for observation in validation_observations:

        comparison = {
            "point_name":
                observation["point_name"],

            "target_x_deg":
                observation["target_x_deg"],

            "target_y_deg":
                observation["target_y_deg"],
        }

        for feature_name in FEATURE_NAMES:

            expected_value = bilinear_interpolate_feature(
                calibration_observations,
                observation["target_x_deg"],
                observation["target_y_deg"],
                feature_name,
            )

            actual_value = observation[
                feature_name
            ]

            delta = (
                actual_value
                - expected_value
            )

            comparison[
                f"{feature_name}_expected"
            ] = expected_value

            comparison[
                f"{feature_name}_actual"
            ] = actual_value

            comparison[
                f"{feature_name}_delta"
            ] = delta

        comparisons.append(
            comparison
        )

    return comparisons

# ============================================================
# Y-ERROR CONTRIBUTION DECOMPOSITION
# ============================================================

def decompose_y_geometry_shift(
    geometry_comparisons,
):
    """
    Decompose the predicted Y shift caused by differences
    between actual validation geometry and the geometry
    expected from the calibration grid.

    For each feature:

        contribution_Y =
            feature_delta * frozen_Y_coefficient

    This is diagnostic only.
    """

    y_coefficients = {
        feature_name:
            CALIBRATION_COEFFICIENTS[
                index + 1,
                1,
            ]
        for index, feature_name
        in enumerate(FEATURE_NAMES)
    }

    decompositions = []

    for comparison in geometry_comparisons:

        contributions = {}

        for feature_name in FEATURE_NAMES:

            delta = comparison[
                f"{feature_name}_delta"
            ]

            contribution = (
                delta
                * y_coefficients[feature_name]
            )

            contributions[
                feature_name
            ] = contribution

        total_contribution = sum(
            contributions.values()
        )

        decompositions.append({
            "point_name":
                comparison["point_name"],

            "target_x_deg":
                comparison["target_x_deg"],

            "target_y_deg":
                comparison["target_y_deg"],

            "left_horizontal_contribution":
                contributions[
                    "left_horizontal_ratio"
                ],

            "right_horizontal_contribution":
                contributions[
                    "right_horizontal_ratio"
                ],

            "left_vertical_contribution":
                contributions[
                    "left_vertical_ratio"
                ],

            "right_vertical_contribution":
                contributions[
                    "right_vertical_ratio"
                ],

            "total_y_shift":
                total_contribution,
        })

    return decompositions

# ============================================================
# MAIN
# ============================================================

def main():

    calibration_gaze = load_gaze_data(
        CALIBRATION_GAZE_FILE
    )

    calibration_events = load_event_data(
        CALIBRATION_EVENT_FILE
    )

    validation_gaze = load_gaze_data(
        VALIDATION_GAZE_FILE
    )

    validation_events = load_event_data(
        VALIDATION_EVENT_FILE
    )

    calibration_observations = build_stable_observations(
        calibration_gaze,
        calibration_events,
    )

    validation_observations = build_stable_observations(
        validation_gaze,
        validation_events,
    )

    geometry_comparisons = compare_validation_geometry(
        calibration_observations,
        validation_observations,
    )

    y_decompositions = decompose_y_geometry_shift(
        geometry_comparisons,
    )

    print(
        "\n=== Phase 1F.3C — Geometry Diagnostic ==="
    )

    print(
        f"\nCalibration observations: "
        f"{len(calibration_observations)}"
    )

    print(
        f"Validation observations: "
        f"{len(validation_observations)}"
    )

    print(
        "\nCalibration stable observations:"
    )

    for observation in calibration_observations:

        print(
            f"{observation['point_name']:<14} "
            f"X={observation['target_x_deg']:+5.1f} "
            f"Y={observation['target_y_deg']:+5.1f} "
            f"N={observation['sample_count']:>2} | "
            f"L-H={observation['left_horizontal_ratio']:.4f} "
            f"R-H={observation['right_horizontal_ratio']:.4f} | "
            f"L-V={observation['left_vertical_ratio']:.4f} "
            f"R-V={observation['right_vertical_ratio']:.4f} | "
            f"L-AP={observation['left_eye_aperture']:.4f} "
            f"R-AP={observation['right_eye_aperture']:.4f}"
        )

    print(
        "\nValidation stable observations:"
    )

    for observation in validation_observations:

        print(
            f"{observation['point_name']:<14} "
            f"X={observation['target_x_deg']:+5.1f} "
            f"Y={observation['target_y_deg']:+5.1f} "
            f"N={observation['sample_count']:>2} | "
            f"L-H={observation['left_horizontal_ratio']:.4f} "
            f"R-H={observation['right_horizontal_ratio']:.4f} | "
            f"L-V={observation['left_vertical_ratio']:.4f} "
            f"R-V={observation['right_vertical_ratio']:.4f} | "
            f"L-AP={observation['left_eye_aperture']:.4f} "
            f"R-AP={observation['right_eye_aperture']:.4f}"
        )

    print(
        "\nValidation geometry delta "
        "(actual - expected):"
    )

    print(
        f"\n{'POINT':<14} | "
        f"{'L-H':>9} "
        f"{'R-H':>9} | "
        f"{'L-V':>9} "
        f"{'R-V':>9}"
    )

    print("-" * 62)

    for comparison in geometry_comparisons:

        print(
            f"{comparison['point_name']:<14} | "
            f"{comparison['left_horizontal_ratio_delta']:>+9.4f} "
            f"{comparison['right_horizontal_ratio_delta']:>+9.4f} | "
            f"{comparison['left_vertical_ratio_delta']:>+9.4f} "
            f"{comparison['right_vertical_ratio_delta']:>+9.4f}"
        )

    print(
        "\nFrozen-model Y contribution decomposition:"
    )

    print(
        f"\n{'POINT':<14} | "
        f"{'L-H':>8} "
        f"{'R-H':>8} "
        f"{'L-V':>8} "
        f"{'R-V':>8} | "
        f"{'TOTAL':>8}"
    )

    print("-" * 68)

    for item in y_decompositions:

        print(
            f"{item['point_name']:<14} | "
            f"{item['left_horizontal_contribution']:>+8.2f} "
            f"{item['right_horizontal_contribution']:>+8.2f} "
            f"{item['left_vertical_contribution']:>+8.2f} "
            f"{item['right_vertical_contribution']:>+8.2f} | "
            f"{item['total_y_shift']:>+8.2f}"
        )

        
if __name__ == "__main__":
    main()