from psychopy import visual, monitors, core, event


MONITOR_NAME = "neuromirror_macbook"

FIXATION_DURATION = 10.0
REST_DURATION = 3.0
TOTAL_BLOCKS = 3


def escape_pressed():
    return "escape" in event.getKeys()


def run_fixation(win, fixation, block_number):
    fixation.draw()

    onset_time = win.flip()

    timer = core.Clock()

    while timer.getTime() < FIXATION_DURATION:
        if escape_pressed():
            return None, True

        fixation.draw()
        win.flip()

    duration = timer.getTime()

    return {
        "block": block_number,
        "onset_time": onset_time,
        "duration": duration
    }, False


def run_rest(win, rest_text):
    rest_text.draw()
    win.flip()

    timer = core.Clock()

    while timer.getTime() < REST_DURATION:
        if escape_pressed():
            return True

        rest_text.draw()
        win.flip()

    return False


def main():
    print("=" * 50)
    print("NeuroMirror Experiment 01")
    print("Phase 1C — Fixation Block Check")
    print("=" * 50)

    monitor = monitors.Monitor(MONITOR_NAME)

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

    rest_text = visual.TextStim(
        win,
        text="Rest",
        pos=(0, 0),
        height=0.7,
        color="black"
    )

    results = []
    aborted = False

    print(f"\nTotal fixation blocks : {TOTAL_BLOCKS}")
    print(f"Fixation duration     : {FIXATION_DURATION:.1f} s")
    print(f"Rest duration         : {REST_DURATION:.1f} s")

    for block in range(1, TOTAL_BLOCKS + 1):

        print(f"\nStarting fixation block {block}...")

        result, aborted = run_fixation(
            win,
            fixation,
            block
        )

        if aborted:
            break

        results.append(result)

        print(
            f"Block {block} completed "
            f"({result['duration']:.4f} s)"
        )

        if block < TOTAL_BLOCKS:
            print("Rest...")
            aborted = run_rest(win, rest_text)

            if aborted:
                break

    win.close()

    print("\n" + "=" * 50)
    print("Fixation Block Summary")
    print("=" * 50)

    for result in results:
        print(
            f"Block {result['block']} : "
            f"{result['duration']:.4f} s"
        )

    if aborted:
        print("\nStatus : ABORTED BY USER")
    else:
        print("\nStatus : COMPLETED")

    print("Fixation block check complete.")


if __name__ == "__main__":
    main()