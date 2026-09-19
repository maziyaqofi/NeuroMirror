from pathlib import Path
import csv

import matplotlib.pyplot as plt


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
# TIME-SERIES PLOT
# ============================================================

def plot_timeseries(samples, events):

    first_onset = events[0]["timestamp"]

    # Only visualize experimental data beginning
    # at the first stimulus onset.
    experiment_samples = [
        sample
        for sample in samples
        if sample["timestamp"] >= first_onset
    ]

    times = [
        sample["timestamp"] - first_onset
        for sample in experiment_samples
    ]

    left_values = [
        sample["left"]
        for sample in experiment_samples
    ]

    right_values = [
        sample["right"]
        for sample in experiment_samples
    ]

    average_values = [
        sample["average"]
        for sample in experiment_samples
    ]

    plt.figure(
        figsize=(14, 7)
    )

    plt.plot(
        times,
        left_values,
        label="Left eye",
        alpha=0.75
    )

    plt.plot(
        times,
        right_values,
        label="Right eye",
        alpha=0.75
    )

    plt.plot(
        times,
        average_values,
        label="Average",
        linewidth=2
    )

    # --------------------------------------------------------
    # STIMULUS ONSETS
    # --------------------------------------------------------

    for stimulus_event in events:

        relative_time = (
            stimulus_event["timestamp"]
            - first_onset
        )

        plt.axvline(
            x=relative_time,
            linestyle="--",
            alpha=0.6
        )

        plt.text(
            relative_time + 0.10,
            0.495,
            stimulus_event["condition"],
            rotation=90,
            verticalalignment="top",
            fontsize=9
        )

    # --------------------------------------------------------
    # PLOT LABELS
    # --------------------------------------------------------

    plt.title(
        "NeuroMirror Phase 1F.1D — "
        "Raw Vertical Iris Signal"
    )

    plt.xlabel(
        "Time from first stimulus onset (s)"
    )

    plt.ylabel(
        "Normalized vertical iris ratio"
    )

    plt.legend()

    plt.grid(
        alpha=0.2
    )

    plt.ylim(
        0.25,
        0.50
    )

    plt.tight_layout()

    plt.show()


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n=== NeuroMirror Phase 1F.1D "
        "— Vertical Time-Series Diagnostic ===\n"
    )

    samples = load_gaze_data()
    events = load_events()

    print(
        f"Loaded gaze samples : {len(samples)}"
    )

    print(
        f"Loaded events       : {len(events)}"
    )

    plot_timeseries(
        samples,
        events
    )


if __name__ == "__main__":
    main()