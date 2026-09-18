from psychopy import visual, monitors, core, event


MONITOR_NAME = "neuromirror_macbook"
TOTAL_FLIPS = 5
INTERVAL = 1.0


def main():
    print("=" * 50)
    print("NeuroMirror Experiment 01")
    print("Phase 1C — callOnFlip Timing Check")
    print("=" * 50)

    monitor = monitors.Monitor(MONITOR_NAME)

    win = visual.Window(
        size=(800, 600),
        fullscr=False,
        monitor=monitor,
        units="deg",
        color="lightgray"
    )

    stimulus = visual.TextStim(
        win,
        text="+",
        pos=(0, 0),
        height=1.0,
        color="black"
    )

    experiment_clock = core.Clock()

    results = []

    def record_flip(flip_number):
        timestamp = experiment_clock.getTime()

        results.append({
            "flip": flip_number,
            "timestamp": timestamp
        })

        print(
            f"[CALLBACK] Flip {flip_number} | "
            f"experiment_time={timestamp:.6f}"
        )

    print("\nRunning callOnFlip diagnostic...\n")

    for flip_number in range(1, TOTAL_FLIPS + 1):

        stimulus.draw()

        win.callOnFlip(
            record_flip,
            flip_number
        )

        win.flip()

        if flip_number < TOTAL_FLIPS:

            timer = core.Clock()

            while timer.getTime() < INTERVAL:

                if "escape" in event.getKeys():
                    win.close()
                    print("\nStatus: ABORTED BY USER")
                    return

                stimulus.draw()
                win.flip()

    win.close()

    print("\n" + "=" * 50)
    print("Recorded Flip Events")
    print("=" * 50)

    for result in results:
        print(
            f"Flip {result['flip']} : "
            f"{result['timestamp']:.6f} s"
        )

    print(f"\nTotal callbacks : {len(results)}")
    print("Status          : COMPLETED")


if __name__ == "__main__":
    main()