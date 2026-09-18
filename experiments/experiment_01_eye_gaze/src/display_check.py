import subprocess
import re


def main():
    print("=" * 50)
    print("NeuroMirror Experiment 01")
    print("Phase 1B — Display Check")
    print("=" * 50)

    try:
        result = subprocess.run(
            ["system_profiler", "SPDisplaysDataType"],
            capture_output=True,
            text=True,
            check=True
        )

        output = result.stdout

        resolution_match = re.search(
            r"Resolution:\s+(\d+)\s+x\s+(\d+)",
            output
        )

        if resolution_match:
            width = int(resolution_match.group(1))
            height = int(resolution_match.group(2))

            print("\nDisplay detected successfully.")
            print(f"Physical resolution : {width} x {height}")
            print(f"Aspect ratio        : {width / height:.3f}")

        else:
            print("\nDisplay detected, but resolution could not be parsed.")
            print("\nRaw display information:")
            print(output)

    except Exception as error:
        print(f"\nERROR: {error}")

    print("\nDisplay check complete.")


if __name__ == "__main__":
    main()