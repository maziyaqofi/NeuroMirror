from psychopy import visual, monitors, core, event


MONITOR_NAME = "neuromirror_macbook"
TOTAL_FLIPS = 5
INTERVAL = 1.0


def main():
    print("=" * 50)
    print("NeuroMirror Experiment 01")
    print("Phase 1C — Flip Timing Check")
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

    print("\nRunning flip timing diagnostic...")
    print(f"Total flips : {TOTAL_FLIPS}")
    print(f"Interval    : {INTERVAL:.1f} s\n")

    results = []

    for flip_number in range(1, TOTAL_FLIPS + 1):

        stimulus.draw()

        # Timestamp associated with the display flip.
        flip_time = win.flip()

        # Timestamp obtained immediately after flip() returns.
        post_flip_time = experiment_clock.getTime()

        results.append({
            "flip": flip_number,
            "flip_time": flip_time,
            "post_flip_time": post_flip_time
        })

        print(
            f"Flip {flip_number} | "
            f"flip_time={flip_time:.6f} | "
            f"post_flip={post_flip_time:.6f}"
        )

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
    print("Timing Comparison")
    print("=" * 50)

    for result in results:

        difference = (
            result["post_flip_time"]
            - result["flip_time"]
        )

        print(
            f"Flip {result['flip']} | "
            f"difference={difference:.6f} s"
        )

    print("\nStatus: COMPLETED")


if __name__ == "__main__":
    main()