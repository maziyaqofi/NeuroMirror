from psychopy import visual, monitors, core, event


MONITOR_NAME = "neuromirror_macbook"

FIXATION_DURATION = 10.0


def main():
    print("=" * 50)
    print("NeuroMirror Experiment 01")
    print("Phase 1C — Fixation Stimulus Check")
    print("=" * 50)

    monitor = monitors.Monitor(MONITOR_NAME)

    print("\nMonitor profile loaded.")
    print(f"Width    : {monitor.getWidth()} cm")
    print(f"Distance : {monitor.getDistance()} cm")
    print(f"Size     : {monitor.getSizePix()}")

    win = visual.Window(
        size=(800, 600),
        fullscr=False,
        monitor=monitor,
        units="deg",
        color="lightgray"
    )

    fixation = visual.TextStim(
        win,
        text="+",
        pos=(0, 0),
        height=1.0,
        color="black"
    )

    fixation.draw()
    win.flip()

    print("\nFixation started.")
    print(f"Target duration: {FIXATION_DURATION:.2f} seconds")

    timer = core.Clock()

    aborted = False

    while timer.getTime() < FIXATION_DURATION:

        if "escape" in event.getKeys():
            aborted = True
            break

        fixation.draw()
        win.flip()

    actual_duration = timer.getTime()

    win.close()

    print(f"Actual duration: {actual_duration:.4f} seconds")

    if aborted:
        print("Status         : ABORTED BY USER")
    else:
        print("Status         : COMPLETED")

    print("\nFixation stimulus check complete.")


if __name__ == "__main__":
    main()