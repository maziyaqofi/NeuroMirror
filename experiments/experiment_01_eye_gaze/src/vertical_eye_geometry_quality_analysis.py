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
# LOWER-TAIL APERTURE ANALYSIS
# ============================================================

def analyze_lower_tail(
    label,
    apertures,
    ratios
):
    """
    Compare vertical-ratio deviation across
    low-aperture portions of the distribution.

    This is descriptive only.
    Percentile boundaries are not QC thresholds.
    """

    median_ratio = statistics.median(
        ratios
    )

    ratio_deviations = [
        abs(ratio - median_ratio)
        for ratio in ratios
    ]

    p05_aperture = percentile(
        apertures,
        5
    )

    p10_aperture = percentile(
        apertures,
        10
    )

    lowest_5 = [
        deviation
        for aperture, deviation
        in zip(apertures, ratio_deviations)
        if aperture <= p05_aperture
    ]

    lowest_10 = [
        deviation
        for aperture, deviation
        in zip(apertures, ratio_deviations)
        if aperture <= p10_aperture
    ]

    remaining_90 = [
        deviation
        for aperture, deviation
        in zip(apertures, ratio_deviations)
        if aperture > p10_aperture
    ]

    print(
        f"\n{label} LOWER-TAIL APERTURE ANALYSIS"
    )

    print(
        f"  P05 aperture boundary : "
        f"{p05_aperture:.6f}"
    )

    print(
        f"  P10 aperture boundary : "
        f"{p10_aperture:.6f}"
    )

    print(
        f"  Lowest 5%  "
        f"N={len(lowest_5):3d} | "
        f"median ratio deviation="
        f"{statistics.median(lowest_5):.6f}"
    )

    print(
        f"  Lowest 10% "
        f"N={len(lowest_10):3d} | "
        f"median ratio deviation="
        f"{statistics.median(lowest_10):.6f}"
    )

    print(
        f"  Remaining 90% "
        f"N={len(remaining_90):3d} | "
        f"median ratio deviation="
        f"{statistics.median(remaining_90):.6f}"
    )

# ============================================================
# EXTREME-DEVIATION CONCENTRATION
# ============================================================

def analyze_extreme_deviation_concentration(
    label,
    apertures,
    ratios
):
    """
    Determine whether the most extreme vertical-ratio
    deviations are concentrated in the lower aperture tail.

    Percentile boundaries are descriptive only.
    They are not QC rejection thresholds.
    """

    median_ratio = statistics.median(
        ratios
    )

    samples = [
        {
            "aperture": aperture,
            "deviation": abs(
                ratio - median_ratio
            ),
        }
        for aperture, ratio
        in zip(apertures, ratios)
    ]

    p05_aperture = percentile(
        apertures,
        5
    )

    p10_aperture = percentile(
        apertures,
        10
    )

    deviations = [
        sample["deviation"]
        for sample in samples
    ]

    p90_deviation = percentile(
        deviations,
        90
    )

    extreme_samples = [
        sample
        for sample in samples
        if sample["deviation"] >= p90_deviation
    ]

    extreme_in_lowest_5 = [
        sample
        for sample in extreme_samples
        if sample["aperture"] <= p05_aperture
    ]

    extreme_in_lowest_10 = [
        sample
        for sample in extreme_samples
        if sample["aperture"] <= p10_aperture
    ]

    total_extreme = len(
        extreme_samples
    )

    pct_lowest_5 = (
        100.0
        * len(extreme_in_lowest_5)
        / total_extreme
    )

    pct_lowest_10 = (
        100.0
        * len(extreme_in_lowest_10)
        / total_extreme
    )

    print(
        f"\n{label} EXTREME-DEVIATION CONCENTRATION"
    )

    print(
        f"  P90 deviation boundary : "
        f"{p90_deviation:.6f}"
    )

    print(
        f"  Extreme samples        : "
        f"{total_extreme}"
    )

    print(
        f"  In lowest 5% aperture  : "
        f"{len(extreme_in_lowest_5)} "
        f"({pct_lowest_5:.1f}%)"
    )

    print(
        f"  In lowest 10% aperture : "
        f"{len(extreme_in_lowest_10)} "
        f"({pct_lowest_10:.1f}%)"
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

    analyze_lower_tail(
        "LEFT",
        left_apertures,
        left_ratios
    )

    analyze_lower_tail(
        "RIGHT",
        right_apertures,
        right_ratios
    )

    analyze_extreme_deviation_concentration(
        "LEFT",
        left_apertures,
        left_ratios
    )

    analyze_extreme_deviation_concentration(
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