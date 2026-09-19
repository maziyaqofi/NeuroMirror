# NeuroMirror Research & Engineering Decisions

## D001 — RGB Camera First

Decision:
Use the MacBook built-in RGB camera for Experiment 01.

Reason:
The first experiment evaluates whether low-cost RGB sensing is
sufficiently stable for longitudinal eye/gaze measurements.

A dedicated eye tracker may later be used as a reference system.

---

## D002 — Speech Excluded as Biomarker

Decision:
Speech analysis is excluded from MVP v1.

Reason:
Reduce multimodal complexity during initial feasibility testing.

Voice may still be used for basic user interaction.

---

## D003 — No Alzheimer's Classification in Experiment 01

Decision:
Experiment 01 will not train or evaluate an Alzheimer's classifier.

Reason:
The first objective is measurement reliability and repeatability,
not clinical classification.

---

## D004 — 14-Day N-of-1 Experiment Design

**Date:** 2026-09-18  
**Status:** Accepted

### Decision

NeuroMirror Experiment 01 will use a **14-day N-of-1 repeated-measurement design** with one developer self-test participant.

The experiment will consist of:

- 14 consecutive days
- 1 session per day
- 14 total sessions

Each daily session will include:

1. environment and camera check
2. 9-point gaze calibration
3. calibration validation
4. fixation task: 3 × 10 seconds
5. short rest
6. prosaccade task: 20 trials
7. short rest
8. antisaccade task: 20 trials
9. session quality check
10. data saving

The participant will be the developer during this initial technical
feasibility experiment.

Development and diagnostic recordings performed before protocol freeze
will not be counted as Day 1 data.

### Rationale

The primary objective of Experiment 01 is to determine whether the
camera-based eye/gaze measurement pipeline can produce repeatable
within-person measurements across repeated daily sessions.

A longitudinal N-of-1 design allows the project to characterize:

- within-person variability
- session-to-session consistency
- measurement repeatability
- tracking quality
- practice or learning effects
- technical outliers

The experiment is designed as an engineering feasibility and
repeatability study rather than a clinical validation study.

Day 1 will not automatically be treated as the participant's baseline.
Baseline interpretation will consider stabilization and possible
practice effects across repeated sessions.

### Consequences

Experiment 01 will not be used to:

- diagnose Alzheimer's disease
- diagnose mild cognitive impairment
- estimate Alzheimer's disease probability or risk
- establish population-level clinical performance
- train an Alzheimer's disease classifier

The initial dataset will represent repeated measurements from one
developer self-test participant.

Any later clinical or population-level study will require a separate
study design, appropriate participants, validation procedures, and
ethical considerations.

The 14-day experiment should begin only after the acquisition,
calibration, task, quality-control, and data-recording procedures are
sufficiently frozen for consistent repeated use.

## D005 — Decouple Stimulus Rendering from Gaze Processing

**Date:** 2026-09-19  
**Status:** Accepted

### Decision

NeuroMirror Experiment 01 will separate stimulus rendering from camera acquisition and gaze processing.

- PsychoPy stimulus rendering and event timing will remain on the **main thread**.
- Camera acquisition and MediaPipe-based gaze processing will run in a **background worker thread**.
- Both components will use the same experiment timebase for timestamping.

### Rationale

Initial integrated testing used a serial loop in which camera acquisition and MediaPipe processing occurred before each PsychoPy display flip.

This architecture degraded stimulus timing:

- Serial-loop PsychoPy median flip interval: **34.56 ms**
- Serial-loop maximum flip interval: **71.61 ms**
- Approximate serial-loop frequency: **20.70 Hz**

A PsychoPy-only baseline demonstrated:

- Median flip interval: **16.67 ms**
- Approximate refresh rate: **59.99 Hz**

After moving camera acquisition and MediaPipe processing to a background worker:

- PsychoPy median flip interval: **16.67 ms**
- Approximate refresh rate: **60.00 Hz**
- Face detection remained operational during gaze processing.

The threaded architecture therefore preserved stimulus presentation timing while allowing gaze processing to operate concurrently.

### Consequences

The experimental architecture will follow:

```text
                 Shared Experiment Clock
                         │
             ┌───────────┴───────────┐
             │                       │
        MAIN THREAD            BACKGROUND WORKER
             │                       │
        PsychoPy                  Camera
        Stimulus                     │
             │                    MediaPipe
        callOnFlip                    │
             │                  Iris Features
             │                       │
             └───────────┬───────────┘
                         │
                  Timestamped Data

---

## D006 — Use ±8° Vertical Target Eccentricity for Current Display Configuration

**Date:** 2026-09-20  
**Status:** Accepted

### Decision

NeuroMirror Experiment 01 will use **±8° vertical target eccentricity**
for the current MacBook display configuration.

The existing horizontal target eccentricity remains **±10°**.

This results in the current two-dimensional target geometry:

- horizontal: ±10°
- vertical: ±8°

### Rationale

The current physical display configuration is:

- active display width: 28.5 cm
- active display height: 17.8 cm
- viewing distance: 52.5 cm

At this viewing distance, the vertical half-height of the active display
is 8.9 cm.

The corresponding center-to-edge vertical visual angle is approximately:

`atan(8.9 / 52.5) ≈ 9.62°`

Therefore, a target positioned at ±10° vertically would exceed the
physical active display area.

A vertical eccentricity of ±8° corresponds to approximately 7.38 cm
from screen center and fits within the available display height with
additional margin.

A PsychoPy fixed-target diagnostic visually confirmed that the +8° and
-8° targets were fully visible in the current display configuration.

### Consequences

For the current Experiment 01 hardware configuration:

- horizontal gaze targets may continue to use ±10°
- vertical gaze targets will use ±8°
- future 2D calibration layouts must respect the asymmetric physical
  display limits
- ±8° should not be interpreted as a biological, clinical, or universal
  gaze-calibration requirement

If the display size or viewing distance changes, the usable visual-angle
range must be recalculated before reusing this value.