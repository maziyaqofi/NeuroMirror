from pathlib import Path
import csv
import statistics


# ============================================================
# INPUT FILES
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

GAZE_FILE = (
    PROJECT_ROOT
    / "data/raw/development"
    / "vertical_visual_gaze_20260920_052311.csv"
)

EVENT_FILE = (
    PROJECT_ROOT
    / "data/raw/development"
    / "vertical_visual_events_20260920_052311.csv"
)


# ============================================================
# DATA LOADING
# ============================================================

def load_gaze_data():

    samples = []

    with GAZE_FILE.open("r") as file:

        reader = csv.DictReader(file)

        for row in reader:

            if not row["average_vertical_ratio"]:
                continue

            samples.append({
                "timestamp": float(row["timestamp"]),
                "left": float(
                    row["left_vertical_ratio"]
                ),
                "right": float(
                    row["right_vertical_ratio"]
                ),
                "average": float(
                    row["average_vertical_ratio"]
                ),
            })

    return samples


def load_events():

    events = []

    with EVENT_FILE.open("r") as file:

        reader = csv.DictReader(file)

        for row in reader:

            events.append({
                "timestamp": float(row["timestamp"]),
                "condition": row["condition"],
                "target_y_deg": float(
                    row["target_y_deg"]
                ),
            })

    return events


# ============================================================
# CONDITION SEGMENTATION
# ============================================================

def segment_conditions(
    samples,
    events
):

    segments = []

    for index, current_event in enumerate(events):

        start_time = current_event["timestamp"]

        if index + 1 < len(events):

            end_time = events[index + 1]["timestamp"]

        else:

            end_time = start_time + 5.0

        condition_samples = [
            sample
            for sample in samples
            if (
                start_time
                <= sample["timestamp"]
                < end_time
            )
        ]

        segments.append({
            "condition": current_event["condition"],
            "target_y_deg": current_event["target_y_deg"],
            "start_time": start_time,
            "end_time": end_time,
            "samples": condition_samples,
        })

    return segments


# ============================================================
# SUMMARY
# ============================================================

def summarize_segment(segment):

    samples = segment["samples"]

    left_values = [
        sample["left"]
        for sample in samples
    ]

    right_values = [
        sample["right"]
        for sample in samples
    ]

    average_values = [
        sample["average"]
        for sample in samples
    ]

    return {
        "condition": segment["condition"],
        "target_y_deg": segment["target_y_deg"],
        "sample_count": len(samples),
        "left_median": statistics.median(left_values),
        "right_median": statistics.median(right_values),
        "average_median": statistics.median(
            average_values
        ),
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n=== NeuroMirror Phase 1F.1D "
        "— Vertical Signal Analysis ===\n"
    )

    samples = load_gaze_data()
    events = load_events()

    print(
        f"Loaded gaze samples : {len(samples)}"
    )

    print(
        f"Loaded events       : {len(events)}"
    )

    segments = segment_conditions(
        samples,
        events
    )

    print(
        "\nCondition-level medians:\n"
    )

    for segment in segments:

        summary = summarize_segment(
            segment
        )

        print(
            f"{summary['condition']:8s} | "
            f"y={summary['target_y_deg']:+.1f} deg | "
            f"N={summary['sample_count']:3d} | "
            f"LEFT={summary['left_median']:.4f} | "
            f"RIGHT={summary['right_median']:.4f} | "
            f"AVG={summary['average_median']:.4f}"
        )


if __name__ == "__main__":
    main()