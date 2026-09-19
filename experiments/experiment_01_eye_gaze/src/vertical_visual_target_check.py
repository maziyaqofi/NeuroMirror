from psychopy import visual, monitors, core, event


# ============================================================
# CONFIGURATION
# ============================================================

MONITOR_NAME = "neuromirror_macbook"

TARGET_ECCENTRICITY = 8.0
CONDITION_DURATION = 5.0

CONDITIONS = [
    ("CENTER_1", 0.0),
    ("TOP", TARGET_ECCENTRICITY),
    ("CENTER_2", 0.0),
    ("BOTTOM", -TARGET_ECCENTRICITY),
    ("CENTER_3", 0.0),
]


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n=== NeuroMirror Phase 1F.1C "
        "— Sequential Vertical Visual Target Check ===\n"
    )

    monitor = monitors.Monitor(
        MONITOR_NAME
    )

    print(
        f"Monitor width    : "
        f"{monitor.getWidth()} cm"
    )

    print(
        f"Viewing distance : "
        f"{monitor.getDistance()} cm"
    )

    print(
        f"Monitor size     : "
        f"{monitor.getSizePix()}"
    )

    print(
        f"\nTarget eccentricity : "
        f"±{TARGET_ECCENTRICITY:.1f} deg"
    )

    print(
        f"Condition duration  : "
        f"{CONDITION_DURATION:.1f} s"
    )

    print(
        "\nSequence:"
    )

    for condition, position_y in CONDITIONS:
        print(
            f"  {condition:8s} "
            f"y={position_y:+.1f} deg"
        )

    win = visual.Window(
        size=(1440, 900),
        fullscr=False,
        monitor=monitor,
        units="deg",
        color="lightgray"
    )

    target = visual.Circle(
        win,
        radius=0.4,
        pos=(0, 0),
        fillColor="black",
        lineColor="black"
    )

    instruction = visual.TextStim(
        win,
        text=(
            "Follow the black dot with your eyes.\n"
            "Keep your head as still as possible.\n"
            "Press ESC to abort."
        ),
        pos=(0, -13),
        height=0.45,
        color="black",
        alignText="center"
    )

    # --------------------------------------------------------
    # READY SCREEN
    # --------------------------------------------------------

    ready_text = visual.TextStim(
        win,
        text=(
            "Vertical target sequence\n\n"
            "CENTER -> TOP -> CENTER "
            "-> BOTTOM -> CENTER\n\n"
            "Press SPACE to start"
        ),
        pos=(0, 0),
        height=0.6,
        color="black",
        alignText="center"
    )

    ready_text.draw()
    win.flip()

    keys = event.waitKeys(
        keyList=["space", "escape"]
    )

    if "escape" in keys:
        win.close()
        print(
            "\nVisual target check aborted."
        )
        return

    # --------------------------------------------------------
    # CONDITION SEQUENCE
    # --------------------------------------------------------

    experiment_clock = core.Clock()

    for condition, position_y in CONDITIONS:

        target.pos = (
            0,
            position_y
        )

        target.draw()
        instruction.draw()

        win.flip()

        onset_time = experiment_clock.getTime()

        print(
            f"\n{condition:8s} | "
            f"y={position_y:+.1f} deg | "
            f"onset={onset_time:.4f} s"
        )

        condition_clock = core.Clock()

        while (
            condition_clock.getTime()
            < CONDITION_DURATION
        ):

            if event.getKeys(
                keyList=["escape"]
            ):
                win.close()

                print(
                    "\nVisual target check aborted."
                )

                return

            core.wait(0.01)

    # --------------------------------------------------------
    # END
    # --------------------------------------------------------

    win.close()

    print(
        "\nSequential visual target check finished."
    )


if __name__ == "__main__":
    main()