from psychopy import monitors


MONITOR_NAME = "neuromirror_macbook"

SCREEN_WIDTH_CM = 28.5
SCREEN_HEIGHT_CM = 17.8
VIEWING_DISTANCE_CM = 52.5

# macOS logical fullscreen resolution observed by PsychoPy
LOGICAL_RESOLUTION = (1440, 900)


def create_monitor_profile():
    monitor = monitors.Monitor(MONITOR_NAME)

    monitor.setWidth(SCREEN_WIDTH_CM)
    monitor.setDistance(VIEWING_DISTANCE_CM)
    monitor.setSizePix(LOGICAL_RESOLUTION)

    monitor.save()

    return monitor


def main():
    print("=" * 50)
    print("NeuroMirror Experiment 01")
    print("Phase 1C — Monitor Configuration")
    print("=" * 50)

    monitor = create_monitor_profile()

    print("\nMonitor profile created successfully.")
    print(f"Name             : {MONITOR_NAME}")
    print(f"Width            : {SCREEN_WIDTH_CM} cm")
    print(f"Measured height  : {SCREEN_HEIGHT_CM} cm")
    print(f"Viewing distance : {VIEWING_DISTANCE_CM} cm")
    print(
        f"Logical resolution: "
        f"{LOGICAL_RESOLUTION[0]} x {LOGICAL_RESOLUTION[1]}"
    )

    print("\nMonitor configuration complete.")


if __name__ == "__main__":
    main()