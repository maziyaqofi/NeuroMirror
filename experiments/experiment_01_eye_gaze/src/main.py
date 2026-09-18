from datetime import datetime
import platform


def main():
    print("=" * 50)
    print("NeuroMirror Experiment 01")
    print("=" * 50)

    print(f"Timestamp : {datetime.now()}")
    print(f"System    : {platform.system()}")
    print(f"Release   : {platform.release()}")
    print(f"Machine   : {platform.machine()}")
    print(f"Processor : {platform.processor()}")

    print("\nEnvironment check complete.")


if __name__ == "__main__":
    main()