import csv
import cv2
import threading
from pathlib import Path
from datetime import datetime

import mediapipe as mp
from psychopy import visual, core


# ============================================================
# CONFIGURATION
# ============================================================

CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_FPS = 30

BLOCK_DURATION_S = 5.0

SEQUENCE = [
    ("CENTER", 0.0),
    ("LEFT", -0.30),
    ("CENTER", 0.0),
    ("RIGHT", 0.30),
    ("CENTER", 0.0),
]

RIGHT_IRIS_CENTER = 468
LEFT_IRIS_CENTER = 473

RIGHT_EYE_OUTER = 33
RIGHT_EYE_INNER = 133

LEFT_EYE_INNER = 362
LEFT_EYE_OUTER = 263


# ============================================================
# SHARED STATE
# ============================================================

experiment_clock = core.Clock()

running = True
gaze_samples = []
stimulus_events = []

lock = threading.Lock()


# ============================================================
# HELPERS
# ============================================================

def normalized_horizontal_position(
    landmarks,
    iris_index,
    corner_a,
    corner_b,
):
    iris_x = landmarks[iris_index].x
    x1 = landmarks[corner_a].x
    x2 = landmarks[corner_b].x

    x_min = min(x1, x2)
    x_max = max(x1, x2)

    width = x_max - x_min

    if width <= 0:
        return None

    return (iris_x - x_min) / width


def gaze_worker():

    global running

    cap = cv2.VideoCapture(CAMERA_INDEX)

    cap.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        CAMERA_WIDTH,
    )

    cap.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        CAMERA_HEIGHT,
    )

    cap.set(
        cv2.CAP_PROP_FPS,
        CAMERA_FPS,
    )

    if not cap.isOpened():
        print("ERROR: Camera could not be opened.")
        running = False
        return

    face_mesh = mp.solutions.face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    frame_number = 0

    while running:

        ret, frame = cap.read()

        if not ret:
            continue

        # Timestamp immediately after frame acquisition.
        timestamp = experiment_clock.getTime()

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB,
        )

        results = face_mesh.process(rgb)

        frame_number += 1

        left_ratio = None
        right_ratio = None
        average_ratio = None
        face_detected = False

        if results.multi_face_landmarks:

            face_detected = True

            landmarks = (
                results
                .multi_face_landmarks[0]
                .landmark
            )

            right_ratio = (
                normalized_horizontal_position(
                    landmarks,
                    RIGHT_IRIS_CENTER,
                    RIGHT_EYE_OUTER,
                    RIGHT_EYE_INNER,
                )
            )

            left_ratio = (
                normalized_horizontal_position(
                    landmarks,
                    LEFT_IRIS_CENTER,
                    LEFT_EYE_INNER,
                    LEFT_EYE_OUTER,
                )
            )

            if (
                left_ratio is not None
                and right_ratio is not None
            ):
                average_ratio = (
                    left_ratio + right_ratio
                ) / 2.0

        sample = {
            "timestamp": timestamp,
            "frame_number": frame_number,
            "face_detected": int(face_detected),
            "left_iris_ratio": left_ratio,
            "right_iris_ratio": right_ratio,
            "average_iris_ratio": average_ratio,
        }

        with lock:
            gaze_samples.append(sample)

    face_mesh.close()
    cap.release()


# ============================================================
# STIMULUS EVENT
# ============================================================

def record_stimulus_onset(
    block_index,
    condition,
):

    timestamp = experiment_clock.getTime()

    with lock:
        stimulus_events.append(
            {
                "timestamp": timestamp,
                "block_index": block_index,
                "condition": condition,
            }
        )


# ============================================================
# START GAZE THREAD
# ============================================================

thread = threading.Thread(
    target=gaze_worker,
    daemon=True,
)

thread.start()


# ============================================================
# PSYCHOPY WINDOW
# ============================================================

win = visual.Window(
    size=(1000, 700),
    fullscr=False,
    units="height",
    color=(0.8, 0.8, 0.8),
)

fixation = visual.Circle(
    win,
    radius=0.008,
    fillColor="black",
    lineColor="black",
)

target = visual.Circle(
    win,
    radius=0.012,
    fillColor="black",
    lineColor="black",
)


# ============================================================
# RUN BLOCKS
# ============================================================

print(
    "\n=== NeuroMirror 1D.3C-10 "
    "— Synchronized Iris Stimulus Test ===\n"
)

print("Keep your head as still as possible.")
print("Look directly at each displayed dot.\n")


for block_index, (condition, x_position) in enumerate(
    SEQUENCE,
    start=1,
):

    target.pos = (
        x_position,
        0.0,
    )

    target.draw()

    win.callOnFlip(
        record_stimulus_onset,
        block_index,
        condition,
    )

    win.flip()

    print(
        f"Block {block_index}: "
        f"{condition}"
    )

    block_clock = core.Clock()

    while (
        block_clock.getTime()
        < BLOCK_DURATION_S
        and running
    ):

        target.draw()
        win.flip()


# ============================================================
# CLEANUP
# ============================================================

running = False
thread.join(timeout=2.0)

win.close()


# ============================================================
# SAVE DATA
# ============================================================

output_dir = Path(
    "data/raw/development"
)

output_dir.mkdir(
    parents=True,
    exist_ok=True,
)

timestamp_string = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

gaze_path = output_dir / (
    f"synchronized_iris_"
    f"{timestamp_string}.csv"
)

event_path = output_dir / (
    f"synchronized_stimulus_"
    f"{timestamp_string}.csv"
)


with gaze_path.open(
    "w",
    newline="",
) as f:

    fieldnames = [
        "timestamp",
        "frame_number",
        "face_detected",
        "left_iris_ratio",
        "right_iris_ratio",
        "average_iris_ratio",
    ]

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames,
    )

    writer.writeheader()
    writer.writerows(gaze_samples)


with event_path.open(
    "w",
    newline="",
) as f:

    fieldnames = [
        "timestamp",
        "block_index",
        "condition",
    ]

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames,
    )

    writer.writeheader()
    writer.writerows(stimulus_events)


# ============================================================
# SUMMARY
# ============================================================

detected = sum(
    sample["face_detected"]
    for sample in gaze_samples
)

total = len(gaze_samples)


print("\n=== RESULTS ===")

print(
    f"Gaze samples recorded: {total}"
)

print(
    f"Stimulus events recorded: "
    f"{len(stimulus_events)}"
)

if total > 0:

    print(
        f"Face detection rate: "
        f"{detected / total * 100:.2f}%"
    )


print("\nStimulus events:")

for event in stimulus_events:

    print(
        f"  Block {event['block_index']} "
        f"{event['condition']:<6} "
        f"{event['timestamp']:.6f} s"
    )


print(
    f"\nGaze CSV:\n  {gaze_path}"
)

print(
    f"\nStimulus CSV:\n  {event_path}"
)

print(
    "\nSynchronized recording diagnostic completed."
)