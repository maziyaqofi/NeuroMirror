from psychopy import visual, monitors, event


MONITOR_NAME = "neuromirror_macbook"


def main():
    print("=" * 50)
    print("NeuroMirror Experiment 01")
    print("Phase 1C — Visual Angle Validation")
    print("=" * 50)

    monitor = monitors.Monitor(MONITOR_NAME)

    print("\nLoaded monitor profile:")
    print(f"Width    : {monitor.getWidth()} cm")
    print(f"Distance : {monitor.getDistance()} cm")
    print(f"Size     : {monitor.getSizePix()}")

    win = visual.Window(
        size=(800, 600),
        fullscr=False,
        monitor=monitor,
        units="deg",
        color="white"
    )

    square = visual.Rect(
        win,
        width=10,
        height=10,
        pos=(0, 0),
        fillColor=None,
        lineColor="black",
        lineWidth=3
    )

    instruction = visual.TextStim(
        win,
        text="10 degree validation\nPress ESC to exit",
        pos=(0, -8),
        height=0.6,
        color="black"
    )

    square.draw()
    instruction.draw()
    win.flip()

    print("\n10-degree stimulus displayed.")
    print("Measure the physical WIDTH of the square.")
    print("Expected width: approximately 9.19 cm")

    event.waitKeys(keyList=["escape"])

    win.close()

    print("\nValidation window closed.")


if __name__ == "__main__":
    main()