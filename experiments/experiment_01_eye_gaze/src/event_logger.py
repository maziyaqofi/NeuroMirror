import csv
from datetime import datetime
from pathlib import Path


class EventLogger:
    """
    Records experiment events using timestamps from
    a shared PsychoPy experiment clock.
    """

    def __init__(self, experiment_clock):
        self.clock = experiment_clock
        self.events = []

    def log_event(
        self,
        event_type,
        task=None,
        block=None,
        trial=None,
        target_direction=None,
        target_eccentricity_deg=None,
        intended_iti_s=None,
        details=None
    ):
        timestamp = self.clock.getTime()

        event = {
            "timestamp": timestamp,
            "event_type": event_type,
            "task": task,
            "block": block,
            "trial": trial,
            "target_direction": target_direction,
            "target_eccentricity_deg": target_eccentricity_deg,
            "intended_iti_s": intended_iti_s,
            "details": details
        }

        self.events.append(event)

        print(
            f"[EVENT] "
            f"{timestamp:.4f}s | "
            f"{event_type} | "
            f"task={task} | "
            f"block={block} | "
            f"trial={trial}"
        )

        return timestamp

    def save_csv(self, output_path):
        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        fieldnames = [
            "timestamp",
            "event_type",
            "task",
            "block",
            "trial",
            "target_direction",
            "target_eccentricity_deg",
            "intended_iti_s",
            "details"
        ]

        with output_path.open(
            "w",
            newline="",
            encoding="utf-8"
        ) as csvfile:

            writer = csv.DictWriter(
                csvfile,
                fieldnames=fieldnames
            )

            writer.writeheader()
            writer.writerows(self.events)

        print(f"\nEvent log saved:")
        print(output_path)


def generate_log_filename():
    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    return f"event_log_{timestamp}.csv"