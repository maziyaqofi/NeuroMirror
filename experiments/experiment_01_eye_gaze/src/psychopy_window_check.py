from psychopy import visual, core


def main():
    print("=" * 50)
    print("NeuroMirror Experiment 01")
    print("Phase 1C — PsychoPy Window Check")
    print("=" * 50)

    print("\nCreating PsychoPy window...")

    win = visual.Window(
        size=(800, 600),
        fullscr=False,
        color="lightgray",
        units="pix"
    )

    print("Window created successfully.")
    print(f"Window size: {win.size}")

    message = visual.TextStim(
        win,
        text="NeuroMirror\n\nPsychoPy Window Test",
        color="black",
        height=30
    )

    message.draw()
    win.flip()

    core.wait(3)

    win.close()

    print("\nWindow closed successfully.")
    print("PsychoPy window check complete.")


if __name__ == "__main__":
    main()