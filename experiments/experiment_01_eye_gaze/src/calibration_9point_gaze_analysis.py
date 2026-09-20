from pathlib import Path
import csv
import statistics

# ============================================================
# DATASET
# ============================================================

DATA_DIR = Path(
    "data/raw/development"
)

GAZE_FILE = DATA_DIR / (
    "calibration_9point_gaze_20260920_064846.csv"
)

EVENT_FILE = DATA_DIR / (
    "calibration_9point_events_20260920_064846.csv"
)

TARGET_DURATION = 2.0

HORIZONTAL_ECCENTRICITY = 10.0
VERTICAL_ECCENTRICITY = 8.0

STABLE_WINDOW_START = 0.300

# ============================================================
# LOAD DATA
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

                "left_eye_width":
                    float(row["left_eye_width"])
                    if row["left_eye_width"]
                    else None,

                "left_vertical_ratio":
                    float(row["left_vertical_ratio"])
                    if row["left_vertical_ratio"]
                    else None,

                "left_eye_aperture":
                    float(row["left_eye_aperture"])
                    if row["left_eye_aperture"]
                    else None,

                "right_horizontal_ratio":
                    float(row["right_horizontal_ratio"])
                    if row["right_horizontal_ratio"]
                    else None,

                "right_eye_width":
                    float(row["right_eye_width"])
                    if row["right_eye_width"]
                    else None,

                "right_vertical_ratio":
                    float(row["right_vertical_ratio"])
                    if row["right_vertical_ratio"]
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
# TARGET SEGMENTATION
# ============================================================

def segment_targets(
    gaze_samples,
    events,
):

    segments = []

    for index, event in enumerate(
        events
    ):

        start_time = (
            event["timestamp"]
        )

        if index < len(events) - 1:

            end_time = (
                events[index + 1][
                    "timestamp"
                ]
            )

        else:

            end_time = (
                start_time
                + TARGET_DURATION
            )

        samples = [
            sample
            for sample in gaze_samples
            if (
                sample["timestamp"]
                >= start_time
                and
                sample["timestamp"]
                < end_time
            )
        ]

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

            "samples":
                samples,
        })

    return segments

def extract_stable_samples(
    segment,
    stable_window_start=STABLE_WINDOW_START,
):
    """
    Extract samples after a provisional post-onset
    transition period.

    This does not modify the raw data and does not
    represent a finalized calibration window.
    """

    stable_start_time = (
        segment["start_time"]
        + stable_window_start
    )

    return [
        sample
        for sample in segment["samples"]
        if sample["timestamp"] >= stable_start_time
        and sample["timestamp"] < segment["end_time"]
    ]

def compare_full_vs_stable_window(
    segment
):
    """
    Compare raw geometry medians from the full target
    interval against the provisional stable interval.

    Full window:
        0.0 s -> end of target

    Stable window:
        STABLE_WINDOW_START -> end of target

    Descriptive analysis only.
    """

    full_samples = [
        sample
        for sample in segment["samples"]
        if sample["face_detected"] == 1
    ]

    stable_samples = [
        sample
        for sample in extract_stable_samples(
            segment
        )
        if sample["face_detected"] == 1
    ]

    fields = [
        "left_horizontal_ratio",
        "right_horizontal_ratio",
        "left_vertical_ratio",
        "right_vertical_ratio",
    ]

    result = {
        "full_n": len(full_samples),
        "stable_n": len(stable_samples),
    }

    for field in fields:

        full_values = [
            sample[field]
            for sample in full_samples
            if sample[field] is not None
        ]

        stable_values = [
            sample[field]
            for sample in stable_samples
            if sample[field] is not None
        ]

        full_median = (
            statistics.median(full_values)
            if full_values
            else None
        )

        stable_median = (
            statistics.median(stable_values)
            if stable_values
            else None
        )

        result[f"{field}_full"] = (
            full_median
        )

        result[f"{field}_stable"] = (
            stable_median
        )

        if (
            full_median is not None
            and stable_median is not None
        ):
            result[f"{field}_difference"] = (
                stable_median
                - full_median
            )
        else:
            result[f"{field}_difference"] = None

    return result

# ============================================================
# TARGET GEOMETRY SUMMARY
# ============================================================

def summarize_target_geometry(
    segment
):
    """
    Calculate raw per-eye median geometry for one
    calibration target segment.

    No smoothing, filtering, aperture rejection,
    or calibration mapping is applied.
    """

    samples = [
        sample
        for sample in segment["samples"]
        if sample["face_detected"] == 1
    ]

    def valid_values(field):

        return [
            sample[field]
            for sample in samples
            if sample[field] is not None
        ]

    left_horizontal = valid_values(
        "left_horizontal_ratio"
    )

    right_horizontal = valid_values(
        "right_horizontal_ratio"
    )

    left_vertical = valid_values(
        "left_vertical_ratio"
    )

    right_vertical = valid_values(
        "right_vertical_ratio"
    )

    left_aperture = valid_values(
        "left_eye_aperture"
    )

    right_aperture = valid_values(
        "right_eye_aperture"
    )

    return {
        "left_horizontal_median":
            statistics.median(
                left_horizontal
            )
            if left_horizontal
            else None,

        "right_horizontal_median":
            statistics.median(
                right_horizontal
            )
            if right_horizontal
            else None,

        "left_vertical_median":
            statistics.median(
                left_vertical
            )
            if left_vertical
            else None,

        "right_vertical_median":
            statistics.median(
                right_vertical
            )
            if right_vertical
            else None,

        "left_aperture_median":
            statistics.median(
                left_aperture
            )
            if left_aperture
            else None,

        "right_aperture_median":
            statistics.median(
                right_aperture
            )
            if right_aperture
            else None,
    }

# ============================================================
# AXIS-LEVEL SEPARABILITY
# ============================================================

def analyze_axis_separability(
    segments
):
    """
    Summarize raw median eye geometry by known
    horizontal and vertical target coordinates.

    This is descriptive only.

    No calibration model, filtering, frame rejection,
    or accuracy criterion is applied.
    """

    summaries = []

    for segment in segments:

        geometry = summarize_target_geometry(
            segment
        )

        summaries.append({
            "x":
                segment["target_x_deg"],

            "y":
                segment["target_y_deg"],

            **geometry,
        })

    horizontal_positions = [
        -HORIZONTAL_ECCENTRICITY,
        0.0,
        +HORIZONTAL_ECCENTRICITY,
    ]

    vertical_positions = [
        +VERTICAL_ECCENTRICITY,
        0.0,
        -VERTICAL_ECCENTRICITY,
    ]

    print(
        "\nHorizontal axis summary:"
    )

    print(
        f"{'X':>6} | "
        f"{'LEFT EYE':>10} "
        f"{'RIGHT EYE':>10}"
    )

    print(
        "-" * 32
    )

    for x_position in horizontal_positions:

        matching = [
            item
            for item in summaries
            if item["x"] == x_position
        ]

        left_values = [
            item["left_horizontal_median"]
            for item in matching
        ]

        right_values = [
            item["right_horizontal_median"]
            for item in matching
        ]

        print(
            f"{x_position:>+6.1f} | "
            f"{statistics.median(left_values):>10.4f} "
            f"{statistics.median(right_values):>10.4f}"
        )

    print(
        "\nVertical axis summary:"
    )

    print(
        f"{'Y':>6} | "
        f"{'LEFT EYE':>10} "
        f"{'RIGHT EYE':>10} | "
        f"{'LEFT AP':>10} "
        f"{'RIGHT AP':>10}"
    )

    print(
        "-" * 58
    )

    for y_position in vertical_positions:

        matching = [
            item
            for item in summaries
            if item["y"] == y_position
        ]

        left_vertical = [
            item["left_vertical_median"]
            for item in matching
        ]

        right_vertical = [
            item["right_vertical_median"]
            for item in matching
        ]

        left_aperture = [
            item["left_aperture_median"]
            for item in matching
        ]

        right_aperture = [
            item["right_aperture_median"]
            for item in matching
        ]

        print(
            f"{y_position:>+6.1f} | "
            f"{statistics.median(left_vertical):>10.4f} "
            f"{statistics.median(right_vertical):>10.4f} | "
            f"{statistics.median(left_aperture):>10.4f} "
            f"{statistics.median(right_aperture):>10.4f}"
        )

# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n=== NeuroMirror Phase 1F.2B "
        "— 9-Point Calibration Segmentation ==="
    )

    gaze_samples = load_gaze_data(
        GAZE_FILE
    )

    events = load_event_data(
        EVENT_FILE
    )

    print(
        f"\nLoaded gaze samples: "
        f"{len(gaze_samples)}"
    )

    print(
        f"Loaded stimulus events: "
        f"{len(events)}"
    )

    segments = segment_targets(
        gaze_samples,
        events,
    )

    print(
        "\nTarget segmentation:"
    )

    for segment in segments:

        samples = segment[
            "samples"
        ]

        face_detected = sum(
            sample["face_detected"]
            for sample in samples
        )

        if samples:

            detection_rate = (
                100.0
                * face_detected
                / len(samples)
            )

        else:

            detection_rate = 0.0

        duration = (
            segment["end_time"]
            - segment["start_time"]
        )

        print(
            f"{segment['point_name']:<14} "
            f"x={segment['target_x_deg']:+5.1f}° "
            f"y={segment['target_y_deg']:+5.1f}° | "
            f"duration={duration:.3f}s | "
            f"N={len(samples):3d} | "
            f"face={detection_rate:5.1f}%"
        )


    # ========================================================
    # RAW PER-TARGET GEOMETRY
    # ========================================================

    print(
        "\nRaw per-target geometry medians:"
    )

    print(
        "\n"
        f"{'POINT':<14} "
        f"{'X':>6} "
        f"{'Y':>6} | "
        f"{'L-H':>8} "
        f"{'R-H':>8} | "
        f"{'L-V':>8} "
        f"{'R-V':>8} | "
        f"{'L-AP':>8} "
        f"{'R-AP':>8}"
    )

    print(
        "-" * 92
    )

    for segment in segments:

        summary = summarize_target_geometry(
            segment
        )

        print(
            f"{segment['point_name']:<14} "
            f"{segment['target_x_deg']:>+6.1f} "
            f"{segment['target_y_deg']:>+6.1f} | "
            f"{summary['left_horizontal_median']:>8.4f} "
            f"{summary['right_horizontal_median']:>8.4f} | "
            f"{summary['left_vertical_median']:>8.4f} "
            f"{summary['right_vertical_median']:>8.4f} | "
            f"{summary['left_aperture_median']:>8.4f} "
            f"{summary['right_aperture_median']:>8.4f}"
        )

    analyze_axis_separability(
        segments
    )

    print(
        "\nFull vs provisional stable-window comparison:"
    )

    print(
        "\n"
        f"{'POINT':<14} "
        f"{'N':>3} "
        f"{'N-ST':>5} | "
        f"{'L-H Δ':>9} "
        f"{'R-H Δ':>9} | "
        f"{'L-V Δ':>9} "
        f"{'R-V Δ':>9}"
    )

    print(
        "-" * 70
    )

    for segment in segments:

        comparison = compare_full_vs_stable_window(
            segment
        )

        print(
            f"{segment['point_name']:<14} "
            f"{comparison['full_n']:>3d} "
            f"{comparison['stable_n']:>5d} | "
            f"{comparison['left_horizontal_ratio_difference']:>+9.5f} "
            f"{comparison['right_horizontal_ratio_difference']:>+9.5f} | "
            f"{comparison['left_vertical_ratio_difference']:>+9.5f} "
            f"{comparison['right_vertical_ratio_difference']:>+9.5f}"
        )

    print(
        "\nProvisional stable-window geometry:"
    )

    print(
        "\n"
        f"{'POINT':<14} "
        f"{'L-H':>9} "
        f"{'R-H':>9} | "
        f"{'L-V':>9} "
        f"{'R-V':>9}"
    )

    print(
        "-" * 58
    )

    for segment in segments:

        comparison = compare_full_vs_stable_window(
            segment
        )

        print(
            f"{segment['point_name']:<14} "
            f"{comparison['left_horizontal_ratio_stable']:>9.4f} "
            f"{comparison['right_horizontal_ratio_stable']:>9.4f} | "
            f"{comparison['left_vertical_ratio_stable']:>9.4f} "
            f"{comparison['right_vertical_ratio_stable']:>9.4f}"
        )


if __name__ == "__main__":
    main()