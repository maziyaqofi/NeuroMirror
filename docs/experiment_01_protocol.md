# NeuroMirror — Experiment 01
## Eye/Gaze Feasibility & Repeatability Pilot

**Protocol Version:** 1.1  
**Status:** Development  
**Study Type:** 14-Day N-of-1 Technical Feasibility Pilot

---

## 1. Objective

The objective of Experiment 01 is to evaluate whether NeuroMirror's
RGB-camera-based eye/gaze pipeline can produce stable, repeatable,
and quality-controlled measurements from the same individual across
repeated daily sessions.

This experiment focuses on measurement feasibility and repeatability.
It does not evaluate Alzheimer's disease, Mild Cognitive Impairment
(MCI), or clinical cognitive decline.

---

## 2. Research Question

Can a camera-based eye/gaze monitoring system reliably capture
eye/gaze behavioral features from the same individual across
14 consecutive daily sessions?

---

## 3. Participant

Number of participants: 1

Participant type:
Developer self-test participant.

Study design:
N-of-1 longitudinal technical feasibility pilot.

The same participant will complete the experiment once per day
for 14 consecutive days.

---

## 4. Study Duration

Duration: 14 consecutive days

Sessions per day: 1

Total planned sessions: 14

Each session should be conducted under approximately consistent
environmental conditions whenever possible.

---

## 5. Hardware

Computer:
MacBook Pro 13-inch (2019)

Processor:
1.4 GHz Quad-Core Intel Core i5

Memory:
8 GB RAM

Camera:
Built-in FaceTime HD RGB camera

Display:
Built-in MacBook Retina display

Initial viewing distance:
Approximately 60 cm

The actual camera resolution, frame rate, and display configuration
will be detected and recorded by the experiment software whenever
possible.

---

## 6. Experimental Tasks

Each daily session consists of:

1. Environment and camera check
2. 9-point gaze calibration
3. Calibration validation
4. Fixation task
5. Short rest
6. Prosaccade task
7. Short rest
8. Antisaccade task
9. Session quality check
10. Data storage

---

## 7. Initial Protocol

### Fixation

3 trials × 10 seconds

The participant maintains gaze on a central fixation point.

Purpose:
- evaluate gaze stability
- evaluate tracking availability
- establish technical reference measurements

### Prosaccade

20 trials per session

- 10 left targets
- 10 right targets
- randomized trial order
- no more than 3 consecutive targets on the same side

Instruction:

"Look at the dot as quickly as you can when it appears."

### Antisaccade

20 trials per session

- 10 left targets
- 10 right targets
- randomized trial order
- no more than 3 consecutive targets on the same side

Instruction:

"Keep looking at the center. When a dot appears on one side,
look in the opposite direction. Do not look at the dot."

---

## 8. Trial Timing

Initial timing:

Fixation:
1000 ms

Peripheral target:
1000 ms

Inter-trial interval:
Randomized between 1000–1500 ms

These values represent Protocol v1 and may be revised after
technical pilot testing.

---

## 9. Target Position

Initial peripheral target eccentricity:

Approximately ±10° visual angle from the center.

Target position should eventually be calculated using:

- screen physical dimensions
- screen resolution
- viewing distance

rather than fixed pixel coordinates.

---

## 10. Calibration

A 9-point calibration procedure will be performed at the beginning
of each daily session.

Calibration points include:

- center
- top-left
- top-center
- top-right
- middle-left
- middle-right
- bottom-left
- bottom-center
- bottom-right

Calibration validation will be performed before the experimental
tasks begin.

Sessions with insufficient calibration quality should trigger
recalibration.

---

## 11. Environment Control

The following conditions should remain approximately consistent
across the 14 sessions:

- same MacBook
- same built-in camera
- same physical location when possible
- approximately 60 cm viewing distance
- similar screen position
- similar lighting conditions
- approximately similar time-of-day window

Environmental differences should be recorded rather than silently
ignored.

---

## 12. Session Metadata

Each session should record:

- participant_id
- session_id
- study_day
- date
- time
- viewing_distance_cm
- camera_device
- camera_resolution
- requested_camera_fps
- measured_camera_fps
- display_resolution
- glasses/contact_lens status
- lighting condition
- calibration quality
- sleep duration (optional contextual metadata)
- recent caffeine intake (optional contextual metadata)
- subjective tiredness (optional contextual metadata)
- notes

Sleep, caffeine, and tiredness are contextual variables only and
are not NeuroMirror cognitive biomarkers.

---

## 13. Planned Dataset

Across 14 sessions, the experiment is expected to produce:

Fixation:
3 × 14 = 42 recordings

Prosaccade:
20 × 14 = 280 trials

Antisaccade:
20 × 14 = 280 trials

Total saccade trials:
560 trials

---

## 14. Primary Technical Measurements

### Tracking Quality

- tracking availability
- missing frame percentage
- gaze confidence
- calibration quality/error
- actual camera frame rate

### Eye/Gaze Measurements

- fixation stability
- response direction
- prosaccade accuracy
- antisaccade accuracy/error rate
- estimated saccadic latency
- gaze movement characteristics

Saccadic latency obtained using the RGB webcam should be treated
as an estimated measurement rather than a clinical-grade
oculomotor measurement.

---

## 15. Longitudinal Analysis

Measurements will be compared across the 14 daily sessions.

The analysis will focus on:

- within-person variability
- session-to-session consistency
- measurement repeatability
- tracking quality
- potential practice/learning effects
- technical outliers

The first session will not automatically be treated as the
participant's definitive baseline.

The experiment will evaluate whether measurements become
sufficiently stable across repeated sessions to support future
development of a personal longitudinal baseline.

---

## 16. Data Structure

Planned structure:

data/
└── raw/
    └── participant_001/
        ├── day_01/
        │   └── session_001/
        ├── day_02/
        │   └── session_002/
        ├── ...
        └── day_14/
            └── session_014/

Each session may contain:

- metadata.json
- calibration.json
- events.csv
- fixation.csv
- prosaccade.csv
- antisaccade.csv
- raw_video.mp4

Raw data should never be manually modified.
Processed data should be stored separately.

---

## 17. Success Criteria

Experiment 01 is considered technically successful if the system
can:

1. Run the complete experimental protocol automatically.
2. Record synchronized stimulus and camera data.
3. Produce usable eye/gaze measurements across repeated sessions.
4. Record objective tracking-quality metrics.
5. Extract the defined gaze features reproducibly.
6. Quantify within-person variability across sessions.
7. Identify technical limitations of the current RGB-camera setup.

Numerical acceptance thresholds will not be predetermined before
initial pilot data are available.

---

## 18. Important Limitations

Experiment 01:

- has only one participant
- is a developer self-test
- is not a clinical study
- does not evaluate Alzheimer's disease
- does not evaluate MCI
- does not validate cognitive decline
- does not establish diagnostic accuracy
- does not produce an Alzheimer's risk score

Results from this experiment should only be interpreted as
technical feasibility and repeatability evidence.

---

## 19. Expected Outcome

At the end of Day 14, Experiment 01 should provide enough
technical evidence to determine whether the current RGB-camera
pipeline is sufficiently stable for further longitudinal
development, requires hardware/software improvement, or should be
validated against a dedicated eye-tracking reference system.