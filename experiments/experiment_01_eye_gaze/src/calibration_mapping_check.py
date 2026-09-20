"""
NeuroMirror Phase 1F.2C
9-Point Calibration Mapping Diagnostic

Purpose
-------
Evaluate whether robust per-target eye geometry from the
9-point calibration run can be mapped to known visual target
coordinates.

This is a development diagnostic only.

It does not establish calibration accuracy, validation
accuracy, or clinical-grade gaze estimation.
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

GAZE_FILE = (
    DATA_DIR
    / "calibration_9point_gaze_20260920_064846.csv"
)

EVENT_FILE = (
    DATA_DIR
    / "calibration_9point_events_20260920_064846.csv"
)

TARGET_DURATION = 2.0

STABLE_WINDOW_START = 0.300


# ============================================================
# MODEL FEATURE DEFINITION
# ============================================================

FEATURE_NAMES = [
    "left_horizontal_ratio",
    "right_horizontal_ratio",
    "left_vertical_ratio",
    "right_vertical_ratio",
]

TARGET_NAMES = [
    "target_x_deg",
    "target_y_deg",
]

# ============================================================
# DATA LOADING
# ============================================================

def load_gaze_data(path):
    samples = []

    with path.open("r", newline="") as file:
        reader = csv.DictReader(file)

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
            })

    return samples


def load_event_data(path):
    events = []

    with path.open("r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            events.append({
                "timestamp":
                    float(row["timestamp"]),

                "event_type":
                    row["event_type"],

                "point_name":
                    row["point_name"],

                "target_x_deg":
                    float(row["target_x_deg"]),

                "target_y_deg":
                    float(row["target_y_deg"]),
            })

    return events

# ============================================================
# CALIBRATION OBSERVATION EXTRACTION
# ============================================================

def build_calibration_observations(
    gaze_samples,
    events,
):
    """
    Build one robust calibration observation per target.

    Each observation uses the median eye geometry from the
    provisional stable window:

        target onset + STABLE_WINDOW_START
        ->
        end of target interval

    Raw data are not modified.
    """

    observations = []

    for index, event in enumerate(events):

        start_time = (
            event["timestamp"]
            + STABLE_WINDOW_START
        )

        if index < len(events) - 1:

            end_time = events[
                index + 1
            ]["timestamp"]

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

            feature_values[
                feature_name
            ] = (
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
        })

    return observations

# ============================================================
# CALIBRATION MATRICES
# ============================================================

def build_calibration_matrices(
    observations
):
    """
    Convert calibration observations into numerical
    feature and target matrices.

    X:
        [L-H, R-H, L-V, R-V]

    Y:
        [target_x_deg, target_y_deg]

    No model fitting is performed here.
    """

    feature_matrix = []

    target_matrix = []

    for observation in observations:

        feature_row = [
            observation[
                feature_name
            ]
            for feature_name in FEATURE_NAMES
        ]

        target_row = [
            observation[
                target_name
            ]
            for target_name in TARGET_NAMES
        ]

        if any(
            value is None
            for value in feature_row
        ):
            raise ValueError(
                "Calibration observation "
                f"{observation['point_name']} "
                "contains missing feature values."
            )

        feature_matrix.append(
            feature_row
        )

        target_matrix.append(
            target_row
        )

    X = np.asarray(
        feature_matrix,
        dtype=float,
    )

    Y = np.asarray(
        target_matrix,
        dtype=float,
    )

    return X, Y

# ============================================================
# LINEAR CALIBRATION MAPPING
# ============================================================

def fit_linear_calibration(
    X,
    Y,
):
    """
    Fit a simple multivariate linear calibration mapping.

    Input features:
        [L-H, R-H, L-V, R-V]

    Targets:
        [X_deg, Y_deg]

    An intercept column is added explicitly.

    This is an in-sample development diagnostic only.
    It is not calibration validation.
    """

    intercept = np.ones(
        (X.shape[0], 1),
        dtype=float,
    )

    X_design = np.hstack(
        [
            intercept,
            X,
        ]
    )

    coefficients, residuals, rank, singular_values = (
        np.linalg.lstsq(
            X_design,
            Y,
            rcond=None,
        )
    )

    predictions = (
        X_design
        @ coefficients
    )

    return {
        "coefficients":
            coefficients,

        "predictions":
            predictions,

        "residuals":
            residuals,

        "rank":
            rank,

        "singular_values":
            singular_values,
    }

# ============================================================
# IN-SAMPLE FIT DIAGNOSTICS
# ============================================================

def calculate_fit_diagnostics(
    observations,
    predictions,
):
    """
    Calculate in-sample residuals for the calibration points.

    These values describe how closely the fitted model
    reproduces the same points used for model fitting.

    They are NOT validation accuracy.
    """

    diagnostics = []

    for observation, prediction in zip(
        observations,
        predictions,
    ):
        predicted_x = float(
            prediction[0]
        )

        predicted_y = float(
            prediction[1]
        )

        error_x = (
            predicted_x
            - observation["target_x_deg"]
        )

        error_y = (
            predicted_y
            - observation["target_y_deg"]
        )

        euclidean_error = float(
            np.sqrt(
                error_x ** 2
                + error_y ** 2
            )
        )

        diagnostics.append({
            "point_name":
                observation["point_name"],

            "target_x_deg":
                observation["target_x_deg"],

            "target_y_deg":
                observation["target_y_deg"],

            "predicted_x_deg":
                predicted_x,

            "predicted_y_deg":
                predicted_y,

            "error_x_deg":
                error_x,

            "error_y_deg":
                error_y,

            "euclidean_error_deg":
                euclidean_error,
        })

    return diagnostics

# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n=== NeuroMirror Phase 1F.2C "
        "— Calibration Observation Check ==="
    )

    gaze_samples = load_gaze_data(
        GAZE_FILE
    )

    events = load_event_data(
        EVENT_FILE
    )

    observations = build_calibration_observations(
        gaze_samples,
        events,
    )

    X, Y = build_calibration_matrices(
        observations
    )

    fit_result = fit_linear_calibration(
        X,
        Y,
    )

    fit_diagnostics = calculate_fit_diagnostics(
        observations,
        fit_result["predictions"],
    )

    print(
        f"\nLoaded gaze samples: "
        f"{len(gaze_samples)}"
    )

    print(
        f"Loaded stimulus events: "
        f"{len(events)}"
    )

    print(
        f"Calibration observations: "
        f"{len(observations)}"
    )

    print(
        "\n"
        f"{'POINT':<14} "
        f"{'X':>6} "
        f"{'Y':>6} "
        f"{'N':>4} | "
        f"{'L-H':>8} "
        f"{'R-H':>8} | "
        f"{'L-V':>8} "
        f"{'R-V':>8}"
    )

    print(
        "-" * 82
    )

    for observation in observations:

        print(
            f"{observation['point_name']:<14} "
            f"{observation['target_x_deg']:>+6.1f} "
            f"{observation['target_y_deg']:>+6.1f} "
            f"{observation['sample_count']:>4d} | "
            f"{observation['left_horizontal_ratio']:>8.4f} "
            f"{observation['right_horizontal_ratio']:>8.4f} | "
            f"{observation['left_vertical_ratio']:>8.4f} "
            f"{observation['right_vertical_ratio']:>8.4f}"
        )

    print(
        "\nCalibration matrix check:"
    )

    print(
        f"X shape: {X.shape}"
    )

    print(
        f"Y shape: {Y.shape}"
    )

    print(
        "\nFeature matrix X:"
    )

    print(X)

    print(
        "\nTarget matrix Y:"
    )

    print(Y)


    print(
        "\nLinear calibration fit diagnostics:"
    )

    print(
        f"Design matrix rank: "
        f"{fit_result['rank']}"
    )

    print(
        "\nSingular values:"
    )

    print(
        fit_result[
            "singular_values"
        ]
    )

    print(
        "\nCoefficient matrix:"
    )

    print(
        fit_result[
            "coefficients"
        ]
    )

    print(
        "\nIn-sample calibration fit:"
    )

    print(
        "\n"
        f"{'POINT':<14} | "
        f"{'TARGET X':>8} "
        f"{'TARGET Y':>8} | "
        f"{'PRED X':>8} "
        f"{'PRED Y':>8} | "
        f"{'ERR X':>8} "
        f"{'ERR Y':>8} | "
        f"{'2D ERR':>8}"
    )

    print("-" * 96)

    for diagnostic in fit_diagnostics:

        print(
            f"{diagnostic['point_name']:<14} | "
            f"{diagnostic['target_x_deg']:>8.2f} "
            f"{diagnostic['target_y_deg']:>8.2f} | "
            f"{diagnostic['predicted_x_deg']:>8.2f} "
            f"{diagnostic['predicted_y_deg']:>8.2f} | "
            f"{diagnostic['error_x_deg']:>+8.2f} "
            f"{diagnostic['error_y_deg']:>+8.2f} | "
            f"{diagnostic['euclidean_error_deg']:>8.2f}"
        )

    euclidean_errors = np.asarray(
        [
            diagnostic["euclidean_error_deg"]
            for diagnostic in fit_diagnostics
        ],
        dtype=float,
    )

    print(
        "\nIn-sample 2D error summary:"
    )

    print(
        f"Mean error:   "
        f"{np.mean(euclidean_errors):.3f} deg"
    )

    print(
        f"Median error: "
        f"{np.median(euclidean_errors):.3f} deg"
    )

    print(
        f"Max error:    "
        f"{np.max(euclidean_errors):.3f} deg"
    )

if __name__ == "__main__":
    main()