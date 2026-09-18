from psychopy import visual, core, event


def main():
    print("=" * 50)
    print("NeuroMirror Experiment 01")
    print("Phase 1C — Fullscreen Check")
    print("=" * 50)

    print("\nCreating fullscreen experiment window...")

    win = visual.Window(
        fullscr=True,
        color="lightgray",
        units="pix"
    )

    print("Fullscreen window created successfully.")
    print(f"Reported window size: {win.size}")

    message = visual.TextStim(
        win,
        text=(
            "NeuroMirror\n\n"
            "Fullscreen Test\n\n"
            "Press ESC to exit"
        ),
        color="black",
        height=30
    )

    message.draw()
    win.flip()

    while True:
        keys = event.getKeys()

        if "escape" in keys:
            break

        core.wait(0.01)

    win.close()

    print("\nESC detected.")
    print("Window closed safely.")
    print("Fullscreen check complete.")


if __name__ == "__main__":
    main()