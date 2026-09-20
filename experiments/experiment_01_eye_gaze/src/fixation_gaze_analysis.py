from pathlib import Path
import csv
import statistics


PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "development"
)


def load_csv(path):
    with path.open(
        "r",
        newline=""
    ) as file:
        return list(
            csv.DictReader(file)
        )


def percentile(values, percentile_value):
    """
    Simple linear-interpolation percentile.
    """

    if not values:
        return None

    sorted_values = sorted(values)

    position = (
        (len(sorted_values) - 1)
        * percentile_value
    )

    lower_index = int(position)
    upper_index = min(
        lower_index + 1,
        len(sorted_values) - 1
    )

    fraction = (
        position - lower_index
    )

    return (
        sorted_values[lower_index]
        + (
            sorted_values[upper_index]
            - sorted_values[lower_index]
        )
        * fraction
    )


def median_absolute_deviation(
    values,
    median_value
):
    deviations = [
        abs(value - median_value)
        for value in values
    ]

    return statistics.median(
        deviations
    )


def find_latest_file(pattern):
    files = list(
        DATA_DIR.glob(pattern)
    )

    if not files:
        raise FileNotFoundError(
            f"No file found for pattern: {pattern}"
        )

    return max(
        files,
        key=lambda path: path.stat().st_mtime
    )


def main():

    gaze_path = find_latest_file(
        "fixation_gaze_*.csv"
    )

    event_path = find_latest_file(
        "fixation_events_*.csv"
    )

    print(
        "\n=== NeuroMirror Phase 1G.2 — Fixation Gaze Analysis ==="
    )

    print(
        f"\nGaze file  : {gaze_path.name}"
    )

    print(
        f"Event file : {event_path.name}"
    )

    gaze_rows = load_csv(
        gaze_path
    )

    event_rows = load_csv(
        event_path
    )

    fixation_events = {}

    for row in event_rows:

        event_type = row[
            "event_type"
        ]

        if event_type not in {
            "fixation_onset",
            "fixation_offset",
        }:
            continue

        block = int(
            row["block"]
        )

        fixation_events.setdefault(
            block,
            {}
        )

        fixation_events[
            block
        ][event_type] = float(
            row["timestamp"]
        )

    print(
        "\n"
        + "=" * 65
    )

    for block in sorted(
        fixation_events
    ):

        events = fixation_events[
            block
        ]

        onset = events.get(
            "fixation_onset"
        )

        offset = events.get(
            "fixation_offset"
        )

        if (
            onset is None
            or offset is None
        ):
            print(
                f"\nBlock {block}: "
                "missing onset/offset event."
            )
            continue

        block_rows = [
            row
            for row in gaze_rows
            if (
                onset
                <= float(
                    row["timestamp"]
                )
                <= offset
            )
        ]

        face_rows = [
            row
            for row in block_rows
            if row[
                "face_detected"
            ] == "1"
        ]

        usable_values = []

        for row in block_rows:

            value = row[
                "average_iris_ratio"
            ]

            if value not in {
                "",
                None,
            }:
                usable_values.append(
                    float(value)
                )

        duration = (
            offset - onset
        )

        total_samples = len(
            block_rows
        )

        face_samples = len(
            face_rows
        )

        usable_samples = len(
            usable_values
        )

        face_rate = (
            (
                face_samples
                / total_samples
            ) * 100
            if total_samples
            else 0.0
        )

        usable_rate = (
            (
                usable_samples
                / total_samples
            ) * 100
            if total_samples
            else 0.0
        )

        sampling_rate = (
            total_samples
            / duration
            if duration > 0
            else 0.0
        )

        print(
            f"\nBlock {block}"
        )

        print(
            f"Duration             : "
            f"{duration:.4f} s"
        )

        print(
            f"Samples              : "
            f"{total_samples}"
        )

        print(
            f"Approx. sample rate  : "
            f"{sampling_rate:.2f} Hz"
        )

        print(
            f"Face detected        : "
            f"{face_samples} "
            f"({face_rate:.2f}%)"
        )

        print(
            f"Usable iris samples  : "
            f"{usable_samples} "
            f"({usable_rate:.2f}%)"
        )

        if not usable_values:

            print(
                "No usable iris values."
            )

            continue

        mean_value = statistics.mean(
            usable_values
        )

        median_value = statistics.median(
            usable_values
        )

        std_value = (
            statistics.stdev(
                usable_values
            )
            if len(usable_values) > 1
            else 0.0
        )

        mad_value = (
            median_absolute_deviation(
                usable_values,
                median_value
            )
        )

        q1 = percentile(
            usable_values,
            0.25
        )

        q3 = percentile(
            usable_values,
            0.75
        )

        iqr = (
            q3 - q1
        )

        print(
            f"Mean iris ratio      : "
            f"{mean_value:.6f}"
        )

        print(
            f"Median iris ratio    : "
            f"{median_value:.6f}"
        )

        print(
            f"Standard deviation   : "
            f"{std_value:.6f}"
        )

        print(
            f"MAD                  : "
            f"{mad_value:.6f}"
        )

        print(
            f"IQR                  : "
            f"{iqr:.6f}"
        )

        print(
            f"Minimum              : "
            f"{min(usable_values):.6f}"
        )

        print(
            f"Maximum              : "
            f"{max(usable_values):.6f}"
        )

    print(
        "\n"
        + "=" * 65
    )

    print(
        "Analysis complete."
    )


if __name__ == "__main__":
    main()