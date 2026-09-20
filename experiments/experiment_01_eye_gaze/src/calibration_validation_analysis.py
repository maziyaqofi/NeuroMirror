"""
NeuroMirror Phase 1F.3B
Independent Calibration Validation Analysis

Purpose
-------
Analyze the independent calibration-validation acquisition.

The validation targets were not used to fit the 9-point
calibration model.

This script first verifies event segmentation and raw data
availability before applying the frozen calibration mapping.

Validation data must not be used to refit or tune the model.
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

GAZE_FILE = DATA_DIR / (
    "calibration_validation_gaze_"
    "20260920_100932.csv"
)

EVENT_FILE = DATA_DIR / (
    "calibration_validation_events_"
    "20260920_100932.csv"
)

STABLE_WINDOW_START = 0.300

FEATURE_NAMES = [
    "left_horizontal_ratio",
    "right_horizontal_ratio",
    "left_vertical_ratio",
    "right_vertical_ratio",
]

TARGET_DURATION = 2.0

CALIBRATION_GAZE_FILE = DATA_DIR / (
    "calibration_9point_gaze_"
    "20260920_064846.csv"
)

CALIBRATION_EVENT_FILE = DATA_DIR / (
    "calibration_9point_events_"
    "20260920_064846.csv"
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
# EVENT SEGMENTATION
# ============================================================

def segment_validation_targets(
    gaze_samples,
    events,
):
    """
    Segment raw gaze samples according to validation
    target presentation intervals.

    For each target:

        start = target onset
        end   = next target onset

    For the final target:

        end = target onset + TARGET_DURATION

    No stable-window exclusion, filtering, smoothing,
    or calibration mapping is applied here.
    """

    segments = []

    for index, event in enumerate(events):

        start_time = event["timestamp"]

        if index < len(events) - 1:

            end_time = (
                events[index + 1]["timestamp"]
            )

        else:

            end_time = (
                event["timestamp"]
                + TARGET_DURATION
            )

        samples = [
            sample
            for sample in gaze_samples
            if sample["timestamp"] >= start_time
            and sample["timestamp"] < end_time
        ]

        detected_samples = [
            sample
            for sample in samples
            if sample["face_detected"] == 1
        ]

        detection_rate = (
            len(detected_samples)
            / len(samples)
            * 100.0
            if samples
            else 0.0
        )

        segments.append({
            "point_name":
                event["point_name"],

            "target_x_deg":
                event["target_x_deg"],

            "target_y_deg":
                event["target_y_deg"],

            "start_time":
                start_time,

            "end_time":
                end_time,

            "duration":
                end_time - start_time,

            "sample_count":
                len(samples),

            "face_detected_count":
                len(detected_samples),

            "face_detection_rate":
                detection_rate,
        })

    return segments

# ============================================================
# VALIDATION OBSERVATION EXTRACTION
# ============================================================

def build_validation_observations(
    gaze_samples,
    events,
):
    """
    Build one robust observation per validation target.

    Uses the same provisional stable-window definition
    as the 9-point calibration mapping:

        target onset + 300 ms
        ->
        end of target interval

    Features are aggregated using the median.

    No calibration mapping is applied here.
    """

    observations = []

    for index, event in enumerate(events):

        start_time = (
            event["timestamp"]
            + STABLE_WINDOW_START
        )

        if index < len(events) - 1:
            end_time = events[index + 1]["timestamp"]
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
# FROZEN CALIBRATION MODEL
# ============================================================

def fit_calibration_model(
    calibration_observations,
):
    """
    Fit the linear calibration mapping using only the
    independent 9-point calibration dataset.

    Validation observations are never used here.

    Features:
        [L-H, R-H, L-V, R-V]

    Targets:
        [X_deg, Y_deg]

    An intercept is added explicitly.
    """

    feature_matrix = []
    target_matrix = []

    for observation in calibration_observations:

        feature_row = [
            observation[feature_name]
            for feature_name in FEATURE_NAMES
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

        target_matrix.append([
            observation["target_x_deg"],
            observation["target_y_deg"],
        ])

    X = np.asarray(
        feature_matrix,
        dtype=float,
    )

    Y = np.asarray(
        target_matrix,
        dtype=float,
    )

    intercept = np.ones(
        (X.shape[0], 1),
        dtype=float,
    )

    X_design = np.hstack([
        intercept,
        X,
    ])

    coefficients, residuals, rank, singular_values = (
        np.linalg.lstsq(
            X_design,
            Y,
            rcond=None,
        )
    )

    return {
        "coefficients": coefficients,
        "rank": rank,
        "singular_values": singular_values,
        "calibration_observation_count":
            len(calibration_observations),
    }

# ============================================================
# VALIDATION PREDICTION
# ============================================================

def predict_validation_targets(
    validation_observations,
    coefficients,
):
    """
    Apply the frozen calibration model to validation
    observations that were not used during model fitting.

    No refitting or parameter tuning is performed.
    """

    predictions = []

    for observation in validation_observations:

        feature_values = [
            observation[feature_name]
            for feature_name in FEATURE_NAMES
        ]

        if any(
            value is None
            for value in feature_values
        ):
            raise ValueError(
                "Validation observation "
                f"{observation['point_name']} "
                "contains missing feature values."
            )

        feature_vector = np.asarray(
            [
                1.0,
                *feature_values,
            ],
            dtype=float,
        )

        predicted_position = (
            feature_vector
            @ coefficients
        )

        predicted_x = float(
            predicted_position[0]
        )

        predicted_y = float(
            predicted_position[1]
        )

        error_x = (
            predicted_x
            - observation["target_x_deg"]
        )

        error_y = (
            predicted_y
            - observation["target_y_deg"]
        )

        error_2d = float(
            np.sqrt(
                error_x ** 2
                + error_y ** 2
            )
        )

        predictions.append({
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

            "error_2d_deg":
                error_2d,
        })

    return predictions

# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n=== NeuroMirror Phase 1F.3B "
        "— Validation Segmentation Check ==="
    )

    gaze_samples = load_gaze_data(
        GAZE_FILE
    )

    events = load_event_data(
        EVENT_FILE
    )

    calibration_gaze_samples = load_gaze_data(
        CALIBRATION_GAZE_FILE
    )

    calibration_events = load_event_data(
        CALIBRATION_EVENT_FILE
    )

    calibration_observations = build_validation_observations(
        calibration_gaze_samples,
        calibration_events,
    )

    calibration_model = fit_calibration_model(
        calibration_observations,
    )

    segments = segment_validation_targets(
        gaze_samples,
        events,
    )

    observations = build_validation_observations(
        gaze_samples,
        events,
    )

    validation_predictions = predict_validation_targets(
        observations,
        calibration_model["coefficients"],
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
        f"Validation segments: "
        f"{len(segments)}"
    )

    print(
        "\n"
        f"{'POINT':<14} "
        f"{'X':>6} "
        f"{'Y':>6} | "
        f"{'DURATION':>8} "
        f"{'N':>4} "
        f"{'FACE':>5} "
        f"{'RATE':>7}"
    )

    print("-" * 68)

    for segment in segments:

        print(
            f"{segment['point_name']:<14} "
            f"{segment['target_x_deg']:>+6.1f} "
            f"{segment['target_y_deg']:>+6.1f} | "
            f"{segment['duration']:>8.3f} "
            f"{segment['sample_count']:>4d} "
            f"{segment['face_detected_count']:>5d} "
            f"{segment['face_detection_rate']:>6.1f}%"
        )

    print(
        "\nValidation stable-window observations:"
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

    print("-" * 82)

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
        "\nFrozen calibration model verification:"
    )

    print(
        f"Calibration observations: "
        f"{calibration_model['calibration_observation_count']}"
    )

    print(
        f"Design matrix rank: "
        f"{calibration_model['rank']}"
    )

    print(
        "\nSingular values:"
    )

    print(
        calibration_model[
            "singular_values"
        ]
    )

    print(
        "\nCoefficient matrix:"
    )

    print(
        calibration_model[
            "coefficients"
        ]
    )

    print(
        "\nIndependent validation predictions:"
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

    for prediction in validation_predictions:

        print(
            f"{prediction['point_name']:<14} | "
            f"{prediction['target_x_deg']:>8.2f} "
            f"{prediction['target_y_deg']:>8.2f} | "
            f"{prediction['predicted_x_deg']:>8.2f} "
            f"{prediction['predicted_y_deg']:>8.2f} | "
            f"{prediction['error_x_deg']:>+8.2f} "
            f"{prediction['error_y_deg']:>+8.2f} | "
            f"{prediction['error_2d_deg']:>8.2f}"
        )

    validation_errors = np.asarray(
        [
            prediction["error_2d_deg"]
            for prediction in validation_predictions
        ],
        dtype=float,
    )

    absolute_x_errors = np.asarray(
        [
            abs(prediction["error_x_deg"])
            for prediction in validation_predictions
        ],
        dtype=float,
    )

    absolute_y_errors = np.asarray(
        [
            abs(prediction["error_y_deg"])
            for prediction in validation_predictions
        ],
        dtype=float,
    )

    print(
        "\nIndependent validation error summary:"
    )

    print(
        f"Mean 2D error:       "
        f"{np.mean(validation_errors):.3f} deg"
    )

    print(
        f"Median 2D error:     "
        f"{np.median(validation_errors):.3f} deg"
    )

    print(
        f"Max 2D error:        "
        f"{np.max(validation_errors):.3f} deg"
    )

    print(
        f"Mean absolute X error: "
        f"{np.mean(absolute_x_errors):.3f} deg"
    )

    print(
        f"Mean absolute Y error: "
        f"{np.mean(absolute_y_errors):.3f} deg"
    )


if __name__ == "__main__":
    main()