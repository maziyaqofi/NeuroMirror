from pathlib import Path
import csv
import statistics

from scipy.stats import spearmanr
# ============================================================
# INPUT FILES
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_DIR = (
    PROJECT_ROOT
    / "data/raw/development"
)

RUN_FILES = [
    DATA_DIR
    / "vertical_eye_geometry_quality_20260920_061217.csv",

    DATA_DIR
    / "vertical_eye_geometry_quality_20260920_061404.csv",
]


# ============================================================
# DATA LOADING
# ============================================================

def load_run(path):

    rows = []

    with path.open("r") as file:

        reader = csv.DictReader(file)

        for row in reader:

            if (
                not row["left_eye_aperture"]
                or not row["right_eye_aperture"]
                or not row["left_vertical_ratio"]
                or not row["right_vertical_ratio"]
            ):
                continue

            rows.append({
                "timestamp": float(
                    row["timestamp"]
                ),

                "frame_number": int(
                    row["frame_number"]
                ),

                "left_aperture": float(
                    row["left_eye_aperture"]
                ),

                "left_ratio": float(
                    row["left_vertical_ratio"]
                ),

                "right_aperture": float(
                    row["right_eye_aperture"]
                ),

                "right_ratio": float(
                    row["right_vertical_ratio"]
                ),
            })

    return rows


# ============================================================
# DESCRIPTIVE STATISTICS
# ============================================================

def percentile(values, percentile_value):

    sorted_values = sorted(values)

    if not sorted_values:
        return None

    position = (
        percentile_value
        / 100.0
        * (len(sorted_values) - 1)
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
        * (1.0 - fraction)
        + sorted_values[upper_index]
        * fraction
    )


def summarize_values(values):

    return {
        "count": len(values),
        "min": min(values),
        "p05": percentile(values, 5),
        "p10": percentile(values, 10),
        "median": statistics.median(values),
        "p90": percentile(values, 90),
        "p95": percentile(values, 95),
        "max": max(values),
    }


def print_summary(
    label,
    summary
):

    print(
        f"\n{label}"
    )

    print(
        f"  N      : {summary['count']}"
    )

    print(
        f"  Min    : {summary['min']:.6f}"
    )

    print(
        f"  P05    : {summary['p05']:.6f}"
    )

    print(
        f"  P10    : {summary['p10']:.6f}"
    )

    print(
        f"  Median : {summary['median']:.6f}"
    )

    print(
        f"  P90    : {summary['p90']:.6f}"
    )

    print(
        f"  P95    : {summary['p95']:.6f}"
    )

    print(
        f"  Max    : {summary['max']:.6f}"
    )

# ============================================================
# APERTURE–RATIO RELATIONSHIP
# ============================================================

def analyze_aperture_ratio_relationship(
    label,
    apertures,
    ratios
):
    """
    Quantify the monotonic relationship between
    eye aperture and vertical-ratio extremeness.

    Ratio extremeness is measured as absolute
    deviation from the run-specific median ratio.

    This is a diagnostic association only.
    It does not define a QC threshold.
    """

    median_ratio = statistics.median(
        ratios
    )

    ratio_deviations = [
        abs(ratio - median_ratio)
        for ratio in ratios
    ]

    correlation, p_value = spearmanr(
        apertures,
        ratio_deviations
    )

    print(
        f"\n{label} "
        "APERTURE vs RATIO DEVIATION"
    )

    print(
        f"  Median ratio       : "
        f"{median_ratio:.6f}"
    )

    print(
        f"  Spearman rho       : "
        f"{correlation:+.4f}"
    )

    print(
        f"  p-value            : "
        f"{p_value:.6g}"
    )

# ============================================================
# RUN ANALYSIS
# ============================================================

def analyze_run(
    path,
    rows
):

    print(
        "\n========================================"
    )

    print(
        f"RUN: {path.name}"
    )

    print(
        "========================================"
    )

    left_apertures = [
        row["left_aperture"]
        for row in rows
    ]

    right_apertures = [
        row["right_aperture"]
        for row in rows
    ]

    left_ratios = [
        row["left_ratio"]
        for row in rows
    ]

    right_ratios = [
        row["right_ratio"]
        for row in rows
    ]

    print_summary(
        "LEFT EYE APERTURE",
        summarize_values(
            left_apertures
        )
    )

    print_summary(
        "RIGHT EYE APERTURE",
        summarize_values(
            right_apertures
        )
    )

    print_summary(
        "LEFT VERTICAL RATIO",
        summarize_values(
            left_ratios
        )
    )

    print_summary(
        "RIGHT VERTICAL RATIO",
        summarize_values(
            right_ratios
        )
    )

    analyze_aperture_ratio_relationship(
        "LEFT",
        left_apertures,
        left_ratios
    )

    analyze_aperture_ratio_relationship(
        "RIGHT",
        right_apertures,
        right_ratios
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n=== NeuroMirror Phase 1F.1E "
        "— Eye Geometry Distribution Analysis ==="
    )

    for path in RUN_FILES:

        rows = load_run(
            path
        )

        print(
            f"\nLoaded {len(rows)} valid "
            f"geometry samples."
        )

        analyze_run(
            path,
            rows
        )


if __name__ == "__main__":
    main()