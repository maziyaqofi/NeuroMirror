from psychopy import visual, core, monitors


# ============================================================
# CONFIGURATION
# ============================================================

MONITOR_NAME = "neuromirror_macbook"

WINDOW_SIZE = (1440, 900)

HORIZONTAL_ECCENTRICITY = 10.0
VERTICAL_ECCENTRICITY = 8.0

TARGET_DURATION = 2.0


# ============================================================
# 9-POINT CALIBRATION LAYOUT
# ============================================================

CALIBRATION_POINTS = [
    ("TOP_LEFT", -HORIZONTAL_ECCENTRICITY, +VERTICAL_ECCENTRICITY),
    ("TOP_CENTER", 0.0, +VERTICAL_ECCENTRICITY),
    ("TOP_RIGHT", +HORIZONTAL_ECCENTRICITY, +VERTICAL_ECCENTRICITY),

    ("MIDDLE_LEFT", -HORIZONTAL_ECCENTRICITY, 0.0),
    ("CENTER", 0.0, 0.0),
    ("MIDDLE_RIGHT", +HORIZONTAL_ECCENTRICITY, 0.0),

    ("BOTTOM_LEFT", -HORIZONTAL_ECCENTRICITY, -VERTICAL_ECCENTRICITY),
    ("BOTTOM_CENTER", 0.0, -VERTICAL_ECCENTRICITY),
    ("BOTTOM_RIGHT", +HORIZONTAL_ECCENTRICITY, -VERTICAL_ECCENTRICITY),
]


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n=== NeuroMirror Phase 1F.2A "
        "— 9-Point Calibration Target Check ==="
    )

    monitor = monitors.Monitor(
        MONITOR_NAME
    )

    win = visual.Window(
        size=WINDOW_SIZE,
        monitor=monitor,
        units="deg",
        fullscr=False,
        color="lightgray",
    )

    target = visual.Circle(
        win=win,
        radius=0.4,
        fillColor="black",
        lineColor="black",
        units="deg",
    )

    experiment_clock = core.Clock()

    print(
        f"\nHorizontal eccentricity: "
        f"±{HORIZONTAL_ECCENTRICITY:.1f}°"
    )

    print(
        f"Vertical eccentricity: "
        f"±{VERTICAL_ECCENTRICITY:.1f}°"
    )

    print(
        f"Target duration: "
        f"{TARGET_DURATION:.1f} s"
    )

    print(
        "\nCalibration sequence:"
    )

    for index, (
        name,
        x_deg,
        y_deg
    ) in enumerate(
        CALIBRATION_POINTS,
        start=1
    ):

        target.pos = (
            x_deg,
            y_deg
        )

        target.draw()

        win.flip()

        onset = experiment_clock.getTime()

        print(
            f"{index:02d}/09 "
            f"{name:<14} "
            f"x={x_deg:+5.1f}° "
            f"y={y_deg:+5.1f}° "
            f"onset={onset:.4f}s"
        )

        core.wait(
            TARGET_DURATION
        )

    win.close()

    print(
        "\n9-point target check complete."
    )


if __name__ == "__main__":
    main()