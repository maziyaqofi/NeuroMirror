from psychopy import visual, monitors, event


MONITOR_NAME = "neuromirror_macbook"


def main():
    print("=" * 50)
    print("NeuroMirror Experiment 01")
    print("Phase 1C — Circle Rendering Check")
    print("=" * 50)

    monitor = monitors.Monitor(MONITOR_NAME)

    win = visual.Window(
        size=(1200, 750),
        fullscr=False,
        monitor=monitor,
        units="deg",
        color="lightgray"
    )

    # Large circle at center.
    center_circle = visual.Circle(
        win,
        radius=2.0,
        pos=(10, 0),
        fillColor="black",
        lineColor="black"
    )

    center_circle.draw()
    win.flip()

    print("\nCircle rendered.")
    print("Expected:")
    print("- Large black circle")
    print("- Position: center of window")
    print("- Radius: 2 degrees")
    print("\nPress ESC to exit.")

    event.waitKeys(keyList=["escape"])

    win.close()

    print("\nCircle rendering check complete.")


if __name__ == "__main__":
    main()