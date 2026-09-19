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