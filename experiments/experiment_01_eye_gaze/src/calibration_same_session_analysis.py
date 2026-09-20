"""
NeuroMirror Phase 1F.4
Same-Session Calibration–Validation Analysis

Purpose
-------
Analyze the same-session calibration-validation development run.

The calibration model must be fitted using only the 9 calibration
targets. The 4 validation targets must remain independent and must
never be used for fitting or tuning.
"""

from pathlib import Path
import csv
import numpy as np

# ============================================================
# CONFIGURATION
# ============================================================

DATA_DIR = Path(
    "data/raw/development"
)

GAZE_FILE = DATA_DIR / (
    "same_session_gaze_"
    "20260920_105430.csv"
)

EVENT_FILE = DATA_DIR / (
    "same_session_events_"
    "20260920_105430.csv"
)

CALIBRATION_TARGET_DURATION = 2.0
VALIDATION_TARGET_DURATION = 2.0

STABLE_WINDOW_START = 0.300

FEATURE_NAMES = [
    "left_horizontal_ratio",
    "right_horizontal_ratio",
    "left_vertical_ratio",
    "right_vertical_ratio",
]


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

                "phase":
                    row["phase"],

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
    Build one stable-window observation for every target
    using the complete same-session event timeline.

    Stable window:
        target onset + 300 ms
        ->
        next stimulus onset

    For the final event:
        target onset + target duration

    Calibration and validation remain labeled by phase.
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

            if event["phase"] == "calibration":
                target_duration = (
                    CALIBRATION_TARGET_DURATION
                )
            else:
                target_duration = (
                    VALIDATION_TARGET_DURATION
                )

            end_time = (
                event["timestamp"]
                + target_duration
            )

        stable_samples = [
            sample
            for sample in gaze_samples
            if sample["timestamp"] >= start_time
            and sample["timestamp"] < end_time
            and sample["face_detected"] == 1
        ]

        observation = {
            "phase":
                event["phase"],

            "point_name":
                event["point_name"],

            "target_x_deg":
                event["target_x_deg"],

            "target_y_deg":
                event["target_y_deg"],

            "sample_count":
                len(stable_samples),
        }

        for feature_name in FEATURE_NAMES:

            values = [
                sample[feature_name]
                for sample in stable_samples
                if sample[feature_name] is not None
            ]

            observation[feature_name] = (
                float(np.median(values))
                if values
                else None
            )

        observations.append(
            observation
        )

    return observations

# ============================================================
# CALIBRATION MODEL FITTING
# ============================================================

def fit_calibration_model(
    observations,
):
    """
    Fit the linear calibration mapping using only
    observations labeled as calibration.

    Validation observations are explicitly excluded.

    Features:
        [L-H, R-H, L-V, R-V]

    Targets:
        [X_deg, Y_deg]

    An intercept is added explicitly.
    """

    calibration_observations = [
        observation
        for observation in observations
        if observation["phase"] == "calibration"
    ]

    if len(calibration_observations) != 9:
        raise ValueError(
            "Expected exactly 9 calibration observations, "
            f"found {len(calibration_observations)}."
        )

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
        "coefficients":
            coefficients,

        "rank":
            rank,

        "singular_values":
            singular_values,

        "calibration_observation_count":
            len(calibration_observations),
    }

# ============================================================
# INDEPENDENT VALIDATION PREDICTION
# ============================================================

def predict_validation_targets(
    observations,
    coefficients,
):
    """
    Apply the frozen same-session calibration model
    to validation observations only.

    Validation observations are not used for fitting
    or model adjustment.
    """

    validation_observations = [
        observation
        for observation in observations
        if observation["phase"] == "validation"
    ]

    if len(validation_observations) != 4:
        raise ValueError(
            "Expected exactly 4 validation observations, "
            f"found {len(validation_observations)}."
        )

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

    gaze_samples = load_gaze_data(
        GAZE_FILE
    )

    events = load_event_data(
        EVENT_FILE
    )

    calibration_events = [
        event
        for event in events
        if event["phase"] == "calibration"
    ]

    validation_events = [
        event
        for event in events
        if event["phase"] == "validation"
    ]

    observations = build_stable_observations(
        gaze_samples,
        events,
    )

    calibration_model = fit_calibration_model(
        observations
    )

    validation_predictions = predict_validation_targets(
        observations,
        calibration_model["coefficients"],
    )

    print(
        "\n=== NeuroMirror Phase 1F.4 — "
        "Same-Session Analysis ==="
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
        f"Calibration events: "
        f"{len(calibration_events)}"
    )

    print(
        f"Validation events: "
        f"{len(validation_events)}"
    )

    print(
        "\nEvent sequence:"
    )

    for index, event in enumerate(
        events,
        start=1,
    ):

        print(
            f"{index:>2}. "
            f"{event['phase']:<11} "
            f"{event['point_name']:<14} "
            f"X={event['target_x_deg']:+5.1f} "
            f"Y={event['target_y_deg']:+5.1f}"
        )

    print(
        "\nStable-window observations:"
    )

    print(
        f"\n{'PHASE':<11} "
        f"{'POINT':<14} "
        f"{'N':>3} | "
        f"{'L-H':>7} "
        f"{'R-H':>7} | "
        f"{'L-V':>7} "
        f"{'R-V':>7}"
    )

    print("-" * 72)

    for observation in observations:

        print(
            f"{observation['phase']:<11} "
            f"{observation['point_name']:<14} "
            f"{observation['sample_count']:>3} | "
            f"{observation['left_horizontal_ratio']:>7.4f} "
            f"{observation['right_horizontal_ratio']:>7.4f} | "
            f"{observation['left_vertical_ratio']:>7.4f} "
            f"{observation['right_vertical_ratio']:>7.4f}"
        )

    print(
        "\nSame-session calibration model:"
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
        "\nSame-session independent validation:"
    )

    print(
        f"\n{'POINT':<14} | "
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

        error_x_values = np.asarray(
        [
            prediction["error_x_deg"]
            for prediction in validation_predictions
        ],
        dtype=float,
    )

    error_y_values = np.asarray(
        [
            prediction["error_y_deg"]
            for prediction in validation_predictions
        ],
        dtype=float,
    )

    error_2d_values = np.asarray(
        [
            prediction["error_2d_deg"]
            for prediction in validation_predictions
        ],
        dtype=float,
    )

    print(
        "\nValidation error summary:"
    )

    print(
        f"Mean absolute X error: "
        f"{np.mean(np.abs(error_x_values)):.3f} deg"
    )

    print(
        f"Mean absolute Y error: "
        f"{np.mean(np.abs(error_y_values)):.3f} deg"
    )

    print(
        f"Mean 2D error: "
        f"{np.mean(error_2d_values):.3f} deg"
    )

    print(
        f"Median 2D error: "
        f"{np.median(error_2d_values):.3f} deg"
    )

    print(
        f"Maximum 2D error: "
        f"{np.max(error_2d_values):.3f} deg"
    )

if __name__ == "__main__":
    main()