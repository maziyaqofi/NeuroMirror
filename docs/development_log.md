# NeuroMirror Development Log

## 2026-09-17
MQ Doc
NeuroMirror Project By Maziya Qofi.

## D004 — 14-Day N-of-1 Experiment Design

Decision:
Experiment 01 will be conducted once per day for 14 consecutive
days using one developer self-test participant.

Reason:
The objective is to evaluate within-person measurement
repeatability and session-to-session variability before expanding
the system to multiple participants or clinical populations.

The experiment is a technical feasibility pilot and must not be
interpreted as evidence of Alzheimer's disease detection or
cognitive decline.

### Phase
Experiment 01 — Phase A

### Goal
Build the first visual stimulus application.

### Completed
- Defined NeuroMirror MVP scope
- Defined Experiment 01
- Defined Stimulus & Trial Protocol v1
- Selected MacBook built-in camera for initial feasibility testing

### Current Work
Building stimulus presentation system.

### Next
Implement fixation stimulus.

### Phase 1A Result

Development environment successfully initialized.

Environment:
- Python: 3.9.6
- Architecture: x86_64
- Operating system: macOS / Darwin 24.6.0
- Virtual environment: .venv
- Project entry point: experiment_01_eye_gaze/src/main.py

Result:
The initial NeuroMirror Experiment 01 application executed
successfully without errors.

### Phase 1B — Device Environment Validation

Camera Acquisition
- Camera successfully accessed through OpenCV.
- Resolution: 1280 × 720
- Requested FPS: 30
- Reported FPS: 30.00
- Initial measured FPS: ~29–30 FPS
- Live camera preview successfully validated.

Display
- Physical display resolution: 2560 × 1600
- Aspect ratio: 1.6

Device Metadata
Automatic device metadata generation successfully implemented.

Output:
`data/device_metadata.json`

The metadata records:
- operating system
- system architecture
- Python environment
- physical display resolution
- camera resolution
- requested FPS
- reported FPS
- measured FPS
- measurement timestamp

Technical Note
The built-in FaceTime HD RGB camera successfully provides
1280 × 720 video at approximately 30 FPS.

This confirms camera acquisition feasibility but does not yet
establish sufficient accuracy or reliability for eye/gaze tracking.

#### Display Detection Issue

Initial display detection using Tkinter caused Python to terminate
because of a Tk/macOS compatibility issue in the current Apple
Command Line Tools Python 3.9.6 environment.

Decision:
Tkinter will not be used by NeuroMirror.

Display hardware information will instead be retrieved using native
macOS system information. Experiment-window dimensions will later be
obtained directly from the stimulus framework.

Impact:
No impact on camera acquisition or Experiment 01 protocol.

### Phase 1C — Visual Angle Validation

Monitor configuration:
- Active display width: 28.5 cm
- Active display height: 17.8 cm
- Viewing distance: 52.5 cm
- PsychoPy monitor resolution: 1440 × 900

A 10-degree visual-angle stimulus was rendered using PsychoPy.

Expected physical width:
~9.19 cm

Measured physical width:
~9.4 cm

Difference:
~0.21 cm (~2.3%)

Result:
PASS for preliminary visual-angle scaling validation.

Note:
Validation was performed in windowed mode because fullscreen
visual presentation on the current macOS/PsychoPy configuration
requires further investigation.

#### Fullscreen Rendering Issue

During Phase 1C, PsychoPy successfully created a fullscreen
experiment window and captured keyboard input. However, visual
stimuli were not visibly rendered on the display.

Observed behavior:
- `fullscr=True` successfully created an experiment window.
- The fullscreen window captured keyboard input.
- ESC successfully terminated the experiment.
- PsychoPy reported a fullscreen framebuffer size of 2880 × 1800.
- macOS reported a logical screen resolution of 1440 × 900.
- Visual stimuli were not visible while fullscreen mode was active.
- The underlying VS Code screen remained visually visible but could
  not be interacted with until ESC was pressed.

Diagnostic test:
The same stimulus was tested using `fullscr=False`.

Result:
- PsychoPy window rendered correctly.
- Rectangle stimulus rendered correctly.
- Text stimulus rendered correctly.
- ESC handling worked correctly.
- Visual-angle stimulus rendered correctly.

This indicates that the issue is specific to fullscreen visual
presentation rather than general PsychoPy stimulus rendering.

Decision:
Development of the stimulus engine will temporarily continue using
windowed mode (`fullscr=False`) while the fullscreen rendering issue
is investigated separately.

Impact:
- No impact on monitor profile creation.
- No impact on preliminary visual-angle validation.
- Fullscreen mode is NOT yet considered validated for Experiment 01.
- The final 14-day experiment will not begin until the display and
  stimulus presentation configuration is frozen and validated.

Status:
UNRESOLVED — does not currently block stimulus engine development.

#### Visual Angle Validation

Monitor configuration:
- Active display width: 28.5 cm
- Active display height: 17.8 cm
- Viewing distance: 52.5 cm
- PsychoPy monitor resolution: 1440 × 900

A 10-degree visual-angle stimulus was rendered using PsychoPy
in windowed mode.

Expected physical width:
~9.19 cm

Measured physical width:
~9.4 cm

Difference:
~0.21 cm (~2.3%)

Result:
PASS for preliminary visual-angle scaling validation.

Note:
The result indicates that no obvious 0.5× or 2× Retina scaling
error was observed in the preliminary physical measurement.

The measured physical monitor dimensions and viewing distance
will not be adjusted merely to force agreement with the theoretical
value. They remain based on direct physical measurements.

Fullscreen visual presentation remains under investigation.

#### Fixation Block Validation

The preliminary fixation protocol was successfully executed using
three consecutive fixation blocks.

Configuration:
- Fixation blocks: 3
- Fixation duration: 10 seconds per block
- Development rest interval: 3 seconds
- Stimulus position: 0° visual angle
- PsychoPy units: degrees
- Rendering mode: windowed

Observed durations:
- Block 1: 10.0008 s
- Block 2: 10.0001 s
- Block 3: 10.0165 s

Result:
PASS

All three fixation blocks completed successfully, including
inter-block rest periods and ESC emergency handling.

Note:
The 3-second rest interval is currently a development parameter
and has not yet been frozen as the final Experiment 01 protocol.

Precise stimulus timing will subsequently be recorded through
a shared experiment clock and structured event logging.

#### Event Logger Validation

A reusable event logging module was implemented to record
experiment events using a shared PsychoPy experiment clock.

The logger records:
- timestamp
- event_type
- task
- block
- trial
- details

A standalone diagnostic test was performed before integrating
the logger with the stimulus tasks.

Test events:
- experiment_start
- fixation_onset
- fixation_offset
- experiment_end

Observed timestamps:
- experiment_start: ~0.0001 s
- fixation_onset: ~1.0001 s
- fixation_offset: ~3.0002 s
- experiment_end: ~4.0003 s

The generated CSV file was manually inspected and confirmed
to contain the expected header, event ordering, timestamps,
and event metadata.

Output location:
`data/raw/development/`

Result:
PASS

Technical decision:
The EventLogger does not create its own experiment clock.
Instead, a shared experiment clock is provided by the
experiment runner. This is intended to support future
synchronization between stimulus events and camera-derived
measurements.

Note:
Full floating-point timestamps are preserved in the raw CSV
rather than rounded display values.

#### Fixation Event Integration

The validated fixation block protocol was integrated with the
shared EventLogger.

Configuration:
- Fixation blocks: 3
- Fixation duration: 10 seconds
- Development rest interval: 3 seconds
- Shared experiment clock: enabled
- Structured event logging: enabled

Recorded events:
- experiment_start
- fixation_onset / fixation_offset
- rest_onset / rest_offset
- experiment_end

A complete test run generated 12 events in the expected order.

Observed timeline:
- Experiment start: 0.0000 s
- Fixation 1 onset: 0.0352 s
- Fixation 1 offset: 10.0376 s
- Fixation 2 onset: 13.0873 s
- Fixation 2 offset: 23.0875 s
- Fixation 3 onset: 26.1206 s
- Fixation 3 offset: 36.1371 s
- Experiment end: 36.1372 s

The event log was successfully saved to:
`data/raw/development/`

Result:
PASS — basic event integration.

Technical observation:
Transitions between several stimulus states were approximately
16–17 ms, which is close to one frame interval on a nominal
60 Hz display. This observation is preliminary and does not
constitute display timing validation.

Timing limitation:
Stimulus onset events are currently logged immediately after
`win.flip()` returns. Therefore, this phase validates event
ordering and shared-clock integration, but does NOT yet establish
frame-accurate stimulus onset timing.

Status:
Basic integration validated.
Precise stimulus timing remains to be validated.

#### Flip Timing Diagnostic

A timing diagnostic was performed to compare timestamps returned
by PsychoPy `win.flip()` with timestamps obtained from the shared
experiment `core.Clock()`.

Five marked display flips were recorded.

Observed timestamps:

| Flip | win.flip() | Experiment Clock |
|------|------------|------------------|
| 1 | 8.791030 s | 0.026004 s |
| 2 | 9.824227 s | 1.059195 s |
| 3 | 10.857621 s | 2.092587 s |
| 4 | 11.890919 s | 3.125901 s |
| 5 | 12.907954 s | 4.142980 s |

The difference between the two timestamp sources remained
approximately constant at 8.765 seconds.

Result:
PASS — timing relationship characterized.

Technical finding:
`win.flip()` timestamps and the shared experiment `core.Clock()`
timestamps do not share the same zero-point in the current
PsychoPy configuration.

Although their progression was highly consistent, raw timestamps
from the two sources must not be directly subtracted without
explicit clock alignment.

Decision:
NeuroMirror will use a single experiment-relative timing reference
for behavioral event logging. Frame-synchronized stimulus onset
logging will be implemented using PsychoPy's flip-synchronized
callback mechanism and the shared experiment clock.

Status:
Clock-origin mismatch identified.
Frame-synchronized shared-clock logging remains to be validated.

#### Frame-Synchronized Callback Validation

PsychoPy's `win.callOnFlip()` mechanism was tested to determine
whether stimulus presentation events could be recorded using the
shared experiment clock at the time of a display flip.

Five callbacks were scheduled across five marked display flips.

Observed callback timestamps:
- Flip 1: 0.025005 s
- Flip 2: 1.041588 s
- Flip 3: 2.075172 s
- Flip 4: 3.108262 s
- Flip 5: 4.141749 s

Total requested callbacks: 5
Total executed callbacks: 5

Result:
PASS

All callbacks executed successfully and produced monotonically
increasing timestamps using the shared experiment clock.

Technical decision:
Stimulus presentation events will use PsychoPy's `callOnFlip()`
mechanism so that event timestamps are captured using the same
experiment-relative clock intended for other NeuroMirror data
streams.

This avoids directly combining raw `win.flip()` timestamps with
`core.Clock()` timestamps, which were previously found to have
different zero-points.

Limitation:
This test validates software-level flip-synchronized event
timestamping. It does not independently measure the physical
photon onset of the display.

Status:
Frame-synchronized shared-clock event timing validated.

#### Flip-Synchronized Fixation Event Integration

The fixation block protocol was integrated with PsychoPy's
`win.callOnFlip()` mechanism and the shared EventLogger.

Configuration:
- Fixation blocks: 3
- Target fixation duration: 10 seconds
- Development rest interval: 3 seconds
- Shared experiment clock: enabled
- Flip-synchronized event logging: enabled

A complete run generated all 12 expected events in the correct
order.

Observed fixation events:
- Block 1 onset: 0.0197 s
- Block 1 offset: 10.0373 s
- Block 2 onset: 13.0871 s
- Block 2 offset: 23.1038 s
- Block 3 onset: 26.1702 s
- Block 3 offset: 36.1869 s

Result:
PASS

All fixation and rest onset/offset events were successfully
recorded through the flip-synchronized callback mechanism using
the shared experiment clock.

Technical observation:
Transitions between fixation offset and rest onset, and between
rest offset and the next fixation onset, were approximately
16–17 ms.

The observed fixation onset-to-offset durations were also
approximately one display frame longer than the nominal
10-second duration.

This behavior is consistent with the current frame-loop and
state-transition implementation and will be considered when
finalizing stimulus timing.

Limitation:
This validation establishes software-level flip-synchronized
event logging. It does not independently verify physical display
photon onset.

Status:
PASS — flip-synchronized structured event logging validated.

#### Single Prosaccade Stimulus Validation

A single prosaccade trial was implemented to validate peripheral
target presentation and flip-synchronized event transitions.

Configuration:
- Trial count: 1
- Target direction: right
- Target eccentricity: +10° visual angle
- Fixation duration: 1.0 s
- Target duration: 1.0 s
- ITI duration: 1.0 s
- Target: black circular stimulus
- Rendering mode: windowed
- Event timing: shared clock + `callOnFlip()`

Observed events:
- fixation_onset: 0.0290 s
- target_onset: 1.0485 s
- target_offset: 2.0651 s
- iti_onset: 2.0652 s
- iti_offset: 3.0983 s

Total events: 7

Result:
PASS — single rightward prosaccade stimulus and event sequence
executed successfully.

Technical observation:
`target_offset` and `iti_onset` were scheduled on the same display
flip and were recorded at effectively the same experiment time
(~0.1 ms difference).

Observed stimulus durations remain influenced by frame-based
presentation timing and have not yet been finalized.

Status:
Rightward +10° prosaccade stimulus validated.
Leftward -10° stimulus remains to be validated.

#### Peripheral Stimulus Clipping Issue

During development of the first prosaccade trial, the central
fixation stimulus was visible, but the +10° peripheral target
was not visibly presented.

A series of rendering diagnostics was performed.

Diagnostic 1:
- Circle radius: 2°
- Position: 0°
- Window: 800 × 600
- Result: circle rendered correctly at the center.

Diagnostic 2:
- Circle radius: 2°
- Position: +10°
- Window: 800 × 600
- Result: circle was rendered but heavily clipped by the
  right boundary of the PsychoPy window.

Diagnostic 3:
- Circle radius: 2°
- Position: +10°
- Window: 1200 × 750
- Result: circle was fully visible.

Finding:
The missing prosaccade target was caused by viewport clipping
in the 800 × 600 development window rather than a failure of
PsychoPy Circle rendering or visual-angle positioning.

Decision:
The ±10° target eccentricity will be preserved.
The stimulus parameter will not be reduced merely to fit the
temporary development window.

A larger window may be used temporarily for stimulus development,
while the final presentation configuration remains unresolved
pending fullscreen investigation.

Status:
ROOT CAUSE IDENTIFIED.
Final experiment display configuration remains unresolved.

#### Single Rightward Prosaccade Validation

Following identification of the viewport clipping issue, the
single prosaccade trial was repeated using a larger development
window.

Configuration:
- Development window: 1200 × 750
- Central fixation: 0°
- Target direction: right
- Target eccentricity: +10°
- Target radius: 0.4°
- Fixation duration: 1.0 s
- Target duration: 1.0 s
- ITI duration: 1.0 s
- Event timing: shared experiment clock + `callOnFlip()`

Visual sequence:
1. Central fixation appeared correctly.
2. The peripheral target appeared clearly on the right.
3. The target was positioned at +10° visual angle.
4. The display transitioned to the blank ITI state.

Result:
PASS — single rightward prosaccade stimulus validated.

Technical note:
The 1200 × 750 window is currently a development configuration,
not the frozen Experiment 01 display configuration.

The final display configuration remains dependent on resolution
of the PsychoPy fullscreen presentation issue.

#### Single Leftward Prosaccade Validation

The single prosaccade trial was repeated using a leftward
peripheral target.

Configuration:
- Development window: 1200 × 750
- Central fixation: 0°
- Target direction: left
- Target eccentricity: -10°
- Target radius: 0.4°
- Fixation duration: 1.0 s
- Target duration: 1.0 s
- ITI duration: 1.0 s

Visual sequence:
1. Central fixation appeared correctly.
2. The peripheral target appeared clearly on the left.
3. The target was positioned at -10° visual angle.
4. The display transitioned to the blank ITI state.

Result:
PASS — single leftward prosaccade stimulus validated.

Combined spatial validation:
Both +10° rightward and -10° leftward prosaccade targets are
visibly presented using the current 1200 × 750 development
window.

Note:
The 1200 × 750 window remains a temporary development
configuration and is not yet the frozen Experiment 01 display
configuration.

#### Balanced Prosaccade Randomization — Single Seed Validation

A balanced LEFT/RIGHT randomization module was implemented for
the prosaccade task.

Configuration:
- Total trials: 20
- LEFT trials: 10
- RIGHT trials: 10
- Maximum consecutive identical directions: 3
- Development test seed: 20260918

Observed result:
- Generation attempts: 4
- Total trials: 20
- LEFT: 10
- RIGHT: 10
- Consecutive constraint: valid

Result:
PASS

The generated sequence satisfied all predefined balancing and
consecutive-direction constraints.

Technical decision:
A local `random.Random(seed)` instance is used rather than
modifying Python's global random state.

Note:
The seed used in this test is a development seed only.
The final per-session seed strategy for Experiment 01 has not
yet been frozen.

Status:
Single-seed randomization validation passed.
Multi-seed and reproducibility validation remain pending.

#### Prosaccade Randomization Robustness Validation

The balanced prosaccade randomization module was further tested
for reproducibility and robustness across multiple random seeds.

Reproducibility test:
- Seed: 20260918
- Two independently generated sequences were compared.
- Result: identical sequences were produced.

Multi-seed robustness test:
- Seeds tested: 100
- Failed seeds: 0
- Maximum generation attempts observed: 13

All generated sequences satisfied:
- 20 total trials
- 10 LEFT trials
- 10 RIGHT trials
- Maximum of 3 consecutive trials in the same direction

Result:
PASS

The randomization module demonstrated deterministic behavior
when provided with the same seed and successfully satisfied all
sequence constraints across 100 tested seeds.

Status:
Balanced prosaccade randomization validated for the current
development requirements.

Note:
The final strategy for assigning random seeds across the 14
Experiment 01 sessions remains to be defined.

#### 4-Trial Prosaccade Integration Validation

A four-trial prosaccade sequence was implemented to validate
multi-trial stimulus presentation and event logging.

Development sequence:
1. RIGHT (+10°)
2. LEFT (-10°)
3. RIGHT (+10°)
4. LEFT (-10°)

Each trial contained:
- Central fixation
- Peripheral target
- Blank inter-trial interval

Configuration:
- Fixation duration: 1.0 s
- Target duration: 1.0 s
- ITI duration: 1.0 s
- Target eccentricity: ±10°
- Target radius: 0.4°
- Development window: 1200 × 750
- Timing: shared experiment clock + `callOnFlip()`

Observed result:
- 4/4 trials completed
- Expected events: 22
- Recorded events: 22
- Event sequence was complete
- Trial identifiers were recorded correctly
- Event log CSV was saved successfully

Result:
PASS — multi-trial prosaccade integration validated.

Timing note:
Observed state durations were approximately 1.0–1.03 seconds,
consistent with the current frame-based development loop.
Final frame-duration control has not yet been frozen.

Note:
The fixed RIGHT-LEFT-RIGHT-LEFT sequence was used only for
integration testing and is not the final experimental
randomization.

Status:
4-trial prosaccade integration validated.

#### Randomizer × Prosaccade Stimulus Integration

The validated balanced randomization module was integrated with
the PsychoPy prosaccade trial engine.

For this development test, a full 20-trial balanced sequence was
generated and only the first four trials were presented.

Configuration:
- Development seed: 20260918
- Full generated sequence: 20 trials
- Presented trials: first 4
- Target eccentricity: ±10°
- Target radius: 0.4°
- Development window: 1200 × 750
- Fixation duration: 1.0 s
- Target duration: 1.0 s
- ITI duration: 1.0 s

Generated first four trials:
1. RIGHT
2. RIGHT
3. RIGHT
4. LEFT

Observed visual presentation:
RIGHT → RIGHT → RIGHT → LEFT

The visual stimulus sequence matched the sequence generated by
the randomization module.

Event logging:
- Expected events: 22
- Recorded events: 22
- Experiment completed without abort
- CSV log saved successfully

Result:
PASS — the validated randomization module successfully controlled
the multi-trial PsychoPy stimulus presentation.

This test also confirmed that three consecutive trials in the
same direction, the maximum allowed by the current randomization
constraint, can be presented correctly.

Status:
Randomizer × stimulus integration validated.

#### Randomized Inter-Trial Interval Validation

A randomized inter-trial interval (ITI) generator was implemented
for the prosaccade task.

Configuration:
- Number of ITIs: 20
- Minimum ITI: 1.0 s
- Maximum ITI: 1.5 s
- Development seed: 20260918
- Sampling method: uniform random distribution

Validation:
- Correct sequence length: PASS
- All generated ITIs within 1.0–1.5 s: PASS
- Same seed reproduced identical ITI sequence: PASS

Observed development test:
- Minimum generated ITI: 1.0548 s
- Maximum generated ITI: 1.4991 s

Result:
PASS — randomized ITI generation validated.

Technical note:
Full floating-point precision is retained internally.
Rounding is used only for human-readable output.

The current seed is a development seed only.
The final session-level random seed strategy remains unfrozen.

#### Randomized ITI × Prosaccade Integration

The validated randomized ITI generator was integrated with the
four-trial prosaccade stimulus engine.

Configuration:
- Development seed: 20260918
- Presented trials: 4
- ITI range: 1.0–1.5 s

Requested ITIs:
- Trial 1: 1.4403 s
- Trial 2: 1.4341 s
- Trial 3: 1.3089 s
- Trial 4: 1.4991 s

Observed event-based ITI durations:
- Trial 1: approximately 1.4667 s
- Trial 2: approximately 1.4665 s
- Trial 3: approximately 1.3333 s
- Trial 4: approximately 1.5166 s

All four trials received their intended randomized ITI values.

An initial integration test revealed that the final ITI value
was unintentionally reused across all trials. The trial execution
loop was corrected to pair each trial direction with its
corresponding ITI using zip(trial_sequence, iti_sequence).

After correction:
- Trial-specific randomized ITIs were correctly applied.
- Direction sequence remained correct.
- 22 expected events were recorded.
- Experiment completed successfully.
- Event log CSV was saved.

Result:
PASS — randomized ITI integration validated.

Timing note:
Observed durations remain quantized by the current frame-based
presentation loop. Final frame-duration control remains unfrozen.

#### Full 20-Trial Prosaccade Block Validation

The complete 20-trial prosaccade development block was executed
successfully.

Configuration:
- Total trials: 20
- LEFT trials: 10
- RIGHT trials: 10
- Maximum consecutive identical directions: 3
- Target eccentricity: ±10°
- Target radius: 0.4°
- Fixation duration: 1.0 s
- Target duration: 1.0 s
- Randomized ITI: 1.0–1.5 s
- Development seed: 20260918
- Development window: 1200 × 750

Two complete development runs were performed.

The second run was specifically observed for visual presentation.

Visual validation:
- Central fixation appeared on every trial.
- Peripheral targets appeared on every trial.
- LEFT and RIGHT targets were presented correctly.
- No fixation stimulus was missing.
- No peripheral target was missing.
- No abnormal visual presentation was observed.

Event validation:
- Trials completed: 20/20
- Expected events: 102
- Recorded events: 102
- Experiment completed without abort.
- Event log CSV was saved successfully.

Result:
PASS — the complete 20-trial prosaccade stimulus block was
successfully executed and visually validated.

Remaining limitations:
- Final display/presentation mode is not yet frozen.
- Fullscreen presentation remains unresolved.
- Final frame-duration control remains unfrozen.
- Camera/eye-tracking integration has not yet begun.

Status:
Full prosaccade development block validated.

### Phase 1C.24 — 4-Trial Randomized Antisaccade Integration

- Integrated generalized antisaccade logic with validated direction randomization.
- Random seed: 20260918.
- Trial sequence: RIGHT, RIGHT, RIGHT, LEFT.
- Expected responses: LEFT, LEFT, LEFT, RIGHT.
- Randomized ITIs: 1.4403, 1.4341, 1.3089, 1.4991 s.
- All four trials completed successfully.
- Event sequence verified for each trial:
  fixation_onset → target_onset → target_offset → iti_onset → iti_offset.
- Total logged events: 22.
- Randomized ITI execution verified.
- Status: PASS.
- Note: behavioral eye responses are not yet objectively measured.

### Phase 1C.25 — Full 20-Trial Antisaccade Block

- Executed the complete 20-trial antisaccade development block.
- Random seed: 20260918.
- Direction balance: 10 RIGHT / 10 LEFT.
- Maximum consecutive same-direction targets: 3.
- Target eccentricity: ±10°.
- Fixation duration: 1.0 s.
- Target duration: 1.0 s.
- ITI randomized between 1.0–1.5 s.
- Antisaccade mapping:
  - RIGHT target → expected LEFT response.
  - LEFT target → expected RIGHT response.
- All 20 trials completed.
- Each trial logged:
  fixation_onset → target_onset → target_offset → iti_onset → iti_offset.
- Total events: 102.
- Status: PASS.

Note:
Behavioral eye responses are not yet objectively measured.
Frame-level timing remains subject to display refresh quantization
and will be addressed during final protocol validation.

### Phase 1C.26 — Full Session Protocol Integration

Goal:
Integrate the previously validated fixation, prosaccade, and
antisaccade stimulus components into one continuous NeuroMirror
Experiment 01 development session using a shared PsychoPy window,
experiment clock, and EventLogger.

#### Phase 1C.26A — Full Session Skeleton

- Created `full_session_protocol_check.py`.
- Established the full session structure:
  session start → fixation → prosaccade → antisaccade → session end.
- Used one shared PsychoPy window, experiment clock, and EventLogger.
- Initial task blocks were represented by placeholders.
- Session skeleton completed successfully.
- Status: PASS.

#### Phase 1C.26B — Real Fixation Integration

- Replaced the fixation placeholder with the validated fixation block.
- Integrated 3 fixation blocks × 10.0 s.
- Development rest duration between fixation blocks: 3.0 s.
- Fixation onset/offset and rest onset/offset were logged.
- All three fixation blocks completed successfully.
- Visual presentation was normal.
- Status: PASS.

Note:
The 3.0 s rest duration remains a development parameter and is not
yet frozen as part of the final experimental protocol.

#### Phase 1C.26C — Real Prosaccade Integration

- Replaced the prosaccade placeholder with the validated 20-trial
  prosaccade block.
- Trials: 20 total.
- Direction balance: 10 RIGHT / 10 LEFT.
- Maximum consecutive identical directions: 3.
- Target eccentricity: ±10°.
- Fixation duration: 1.0 s.
- Target duration: 1.0 s.
- Randomized ITI: 1.0–1.5 s.
- Development seed: 20260918.
- Each trial logged:
  fixation_onset → target_onset → target_offset → iti_onset → iti_offset.
- All 20 trials completed successfully.
- Central fixation and peripheral targets were visually confirmed
  on all trials.
- No missing, frozen, or abnormal stimulus presentation was observed.
- Status: PASS.

#### Phase 1C.26D — Real Antisaccade Integration

- Replaced the antisaccade placeholder with the validated 20-trial
  antisaccade block.
- Trials: 20 total.
- Direction balance: 10 RIGHT / 10 LEFT.
- Maximum consecutive identical directions: 3.
- Antisaccade mapping:
  - RIGHT target → expected LEFT response.
  - LEFT target → expected RIGHT response.
- Target eccentricity: ±10°.
- Fixation duration: 1.0 s.
- Target duration: 1.0 s.
- Randomized ITI: 1.0–1.5 s.
- Development seed: 20260918.
- Each trial logged:
  fixation_onset → target_onset → target_offset → iti_onset → iti_offset.
- All 20 trials completed successfully.
- Stimulus presentation was visually confirmed as normal.
- Opposite-direction antisaccade instructions could be followed
  throughout the block.
- Status: PASS.

#### Full Session Validation

The complete integrated development session successfully executed:

1. Session start
2. Fixation — 3 × 10 s
3. Prosaccade — 20 trials
4. Antisaccade — 20 trials
5. Session end
6. Event log CSV saved successfully

Expected logical event count:
Event log validation:
- Expected logical event count: 212.
- Recorded event count: 212.
- Session events: 2.
- Fixation/rest events: 10.
- Prosaccade events: 100 across 20 trials.
- Antisaccade events: 100 across 20 trials.
- Prosaccade direction balance: 10 RIGHT / 10 LEFT.
- Antisaccade target balance: 10 RIGHT / 10 LEFT.
- All 40 saccade trials contained the expected five-event sequence:
  fixation_onset → target_onset → target_offset → iti_onset → iti_offset.
- Event timestamps were monotonically increasing.
- No missing trial event sequence was detected.
- Validation source: event_log_20260918_140312.csv.

Result:
PASS — fixation, prosaccade, and antisaccade stimulus protocols were
successfully integrated into one continuous development session.

Important limitations:
- Behavioral eye responses are not yet objectively measured.
- Camera/eye-gaze tracking is not yet integrated.
- Fullscreen visual presentation remains unresolved.
- Final frame-duration control remains unfrozen.
- Current event timing represents software-level flip-synchronized
  timing, not physical photon-onset validation.
- Final experimental presentation parameters are not yet frozen.
- This development run is not part of the 14-day Experiment 01 dataset.

Status:
Phase 1C.26 Full Session Protocol Integration validated.

---

## Phase 1D — Eye/Gaze Tracking Development

### 1D.1A — Camera Acquisition Sanity Check

**Status:** PASS

The built-in FaceTime HD camera was tested using OpenCV before integrating eye/gaze tracking.

Observed configuration:

- Resolution: 1280 × 720
- Requested FPS: 30
- Reported FPS: 30.00
- Measured FPS: approximately 29.93
- Test duration: approximately 5 seconds
- Captured frames: 150

The camera acquisition pipeline operated successfully and was considered sufficient to continue with gaze-tracking feasibility testing.

---

### 1D.1B — Isolated Gaze Tracking Environment

**Status:** PASS

MediaPipe compatibility was evaluated before installation into the main NeuroMirror environment.

A dry-run installation indicated that MediaPipe would modify important dependencies in the existing `.venv311` environment, including NumPy and the OpenCV stack.

To preserve the stable PsychoPy environment, a separate gaze-tracking sandbox was created:

- Environment: `.venv_gaze_test`
- Python: 3.11.16
- MediaPipe: 0.10.21
- OpenCV: 4.11.0
- NumPy: 1.26.4

This environment is used for current MediaPipe-based eye/gaze feasibility development.

---

### 1D.1C — Gaze Environment Dependency Verification

**Status:** PASS

The core gaze-tracking dependencies were successfully imported inside `.venv_gaze_test`.

Verified packages:

- MediaPipe 0.10.21
- OpenCV 4.11.0
- NumPy 1.26.4

No import failure occurred.

---

### 1D.1D — Face and Eye/Iris Landmark Detection

**Status:** PASS

MediaPipe Face Mesh was tested using the built-in RGB camera with refined facial landmarks enabled.

The system successfully detected:

- Face landmarks
- Eye landmarks
- Iris landmarks

During manual observation, iris landmarks visually followed eye movement.

This test confirms landmark detection feasibility only. It does not establish gaze-direction accuracy or clinical-grade eye tracking.

---

### 1D.2A — Normalized Horizontal Iris Position Signal

**Status:** PRELIMINARY PASS

A normalized horizontal iris-position feature was calculated relative to the eye-corner landmarks.

Manual observations at approximately 52.5 cm viewing distance showed:

- CENTER: approximately 0.470–0.525
- RIGHT: approximately 0.438–0.489
- LEFT: approximately 0.500–0.578

The observed ordering was:

`RIGHT < CENTER < LEFT`

However, the ranges overlapped. Therefore, no fixed gaze-direction thresholds were defined.

The result suggests that normalized iris position contains a usable horizontal gaze signal, but classification performance remains unvalidated.

---

### 1D.2B — Automatic Iris Signal Recording

**Status:** PASS

A frame-level recording diagnostic was implemented to automatically collect normalized iris-position measurements during a controlled sequence:

`CENTER → LEFT → CENTER → RIGHT → CENTER`

Each condition lasted approximately 5 seconds.

Recorded fields included:

- Timestamp
- Frame number
- Condition
- Left iris ratio
- Right iris ratio
- Average iris ratio
- Face detection status

Raw video was not stored.

#### Stable Development Run

File:

`iris_signal_20260919_044923.csv`

Results:

- Total frames: 389
- Face detected: 389
- Tracking availability: 100%
- Missing iris measurements: 0

Median average iris ratios:

- LEFT: 0.5591
- CENTER: 0.5080
- RIGHT: 0.4672

The expected directional ordering was reproduced:

`RIGHT < CENTER < LEFT`

Raw frame-level distributions still overlapped. Therefore, these results do not support fixed per-frame LEFT/CENTER/RIGHT classification thresholds.

#### Tracking-Loss Development Run

File:

`iris_signal_20260919_045233.csv`

The participant intentionally moved partially or completely outside the camera view during the recording.

Results:

- Total frames: 414
- Face detected: 111
- Tracking availability: 26.81%

This run demonstrated that the recording pipeline can represent loss of face tracking quantitatively.

Tracking availability may therefore become one component of future session-level quality control.

---

### 1D.2C — Block-Level Signal Repeatability

**Status:** PRELIMINARY PASS

A second diagnostic preserved each condition as an independent block:

1. CENTER
2. LEFT
3. CENTER
4. RIGHT
5. CENTER

This allowed the three CENTER measurements to be evaluated independently.

#### Tracking-Loss Run

File:

`iris_block_repeatability_20260919_050619.csv`

Results:

- Total frames: 458
- Face detected: 251
- Tracking availability: 54.80%

The participant was not consistently visible to the camera during this run.

The run is retained as development evidence of tracking loss and is not used as the primary repeatability run.

#### Stable Repeatability Run

File:

`iris_block_repeatability_20260919_064229.csv`

Results:

- Total frames: 393
- Face detected: 393
- Tracking availability: 100%

Block-level median average iris ratios:

| Block | Condition | Median |
|------:|-----------|-------:|
| 1 | CENTER | 0.4976 |
| 2 | LEFT | 0.5415 |
| 3 | CENTER | 0.4990 |
| 4 | RIGHT | 0.4507 |
| 5 | CENTER | 0.4981 |

CENTER medians:

- CENTER-1: 0.4976
- CENTER-2: 0.4990
- CENTER-3: 0.4981

CENTER median range:

`0.0014`

Directional ordering was again observed:

`RIGHT < CENTER < LEFT`

The three CENTER blocks returned to very similar median values during this recording, providing preliminary evidence of short-term within-session repeatability.

Absolute iris-ratio values differed between development runs while directional ordering remained consistent. This observation supports investigating session-specific or personalized reference measurements rather than assuming universal fixed thresholds.

Frame-level ranges continued to overlap across gaze conditions. Future processing should therefore investigate temporal aggregation and calibration rather than relying on individual-frame classification.

---

## Phase 1D Current Interpretation

Development testing currently supports the following conclusions:

1. The built-in RGB camera can provide face and iris landmarks using MediaPipe.
2. Normalized horizontal iris position responds systematically to horizontal gaze movement.
3. The directional pattern `RIGHT < CENTER < LEFT` has been reproduced across multiple development runs.
4. Short-term repeated CENTER measurements showed promising within-session consistency in the stable repeatability run.
5. Face-tracking loss can be detected and quantified.
6. Individual frame values are not sufficiently separated to justify fixed gaze-direction thresholds.
7. Absolute iris-ratio values can shift between recordings.
8. Session-specific calibration and relative gaze displacement should be investigated before gaze classification.
9. These results demonstrate engineering feasibility only and do not establish clinical validity or Alzheimer’s-related biomarker validity.

### Phase 1D.2 Overall Status

**Eye/Iris Horizontal Signal Feasibility: PRELIMINARY PASS**

The next development stage should focus on converting the raw iris-position signal into a calibrated, temporally robust gaze representation suitable for controlled fixation and saccade tasks.

## 2026-09-19 — Phase 1D.3C: Integrated Stimulus–Gaze Timing Pipeline

### Objective

Evaluate whether PsychoPy stimulus presentation, RGB camera acquisition, MediaPipe FaceMesh processing, iris-position extraction, and stimulus-event timing can operate within a synchronized experimental pipeline suitable for later eye/gaze tasks.

This phase focused on engineering feasibility and temporal synchronization. It did not attempt to validate clinical-grade eye tracking or saccadic latency measurement.

---

### Integrated Environment

A dedicated integrated environment was created:

- Environment: `.venv_experiment`
- Python: 3.11.16
- PsychoPy: 2026.2.4
- MediaPipe: 0.10.21
- NumPy: 1.26.4
- OpenCV: 4.11.0

PsychoPy, OpenCV camera acquisition, and MediaPipe FaceMesh were successfully imported and executed within the same environment.

---

### Serial Processing Timing Test

Initial integration used a serial processing loop:

1. Capture camera frame
2. Run MediaPipe processing
3. Render PsychoPy frame
4. Flip display

Results:

- MediaPipe processing mean: 10.57 ms
- MediaPipe processing median: 10.65 ms
- Maximum MediaPipe processing time: 50.34 ms
- Complete loop mean: 48.31 ms
- PsychoPy flip interval median: 34.56 ms
- PsychoPy flip interval maximum: 71.61 ms
- Approximate loop frequency: 20.70 Hz

This architecture substantially disrupted PsychoPy display timing and was therefore not considered suitable for the experimental pipeline.

---

### PsychoPy Timing Baseline

A PsychoPy-only timing test was performed to establish the display baseline.

Results:

- Total flips: 299
- Mean flip interval: 16.67 ms
- Median flip interval: 16.67 ms
- Minimum: 14.58 ms
- Maximum: 18.57 ms
- Approximate refresh rate: 59.99 Hz

The result confirmed that PsychoPy itself could maintain approximately 60 Hz timing.

---

### Threaded Architecture

Camera acquisition and MediaPipe processing were moved to a background worker while PsychoPy stimulus rendering remained on the main thread.

Camera-only threaded test:

- PsychoPy flips: 300
- Median flip interval: 16.66 ms
- Approximate refresh rate: 60.03 Hz

Camera + MediaPipe threaded test:

- PsychoPy flips: 300
- MediaPipe frames processed: 206
- Face detection: 100%
- MediaPipe processing mean: 5.33 ms
- MediaPipe processing median: 4.97 ms
- Maximum MediaPipe processing time: 55.88 ms
- PsychoPy flip interval median: 16.67 ms
- Approximate refresh rate: 60.00 Hz

The threaded architecture preserved PsychoPy timing despite occasional longer MediaPipe processing times.

---

### Shared Clock Verification

A single PsychoPy `core.Clock()` was shared between the main stimulus thread and the background worker.

Stimulus onset was timestamped using `win.callOnFlip()`.

Example verification:

- Stimulus onset: 3.468990 s
- Nearest worker sample before onset: 4.33 ms earlier
- Nearest worker sample after onset: 5.86 ms later

This demonstrated that stimulus and worker events could be represented within the same software timebase.

These differences represent sample proximity in the diagnostic test and must not be interpreted as gaze measurement accuracy or end-to-end synchronization error.

---

### Synchronized Iris–Stimulus Recording

A synchronized diagnostic pipeline was implemented in:

`experiments/experiment_01_eye_gaze/src/synchronized_iris_stimulus_check.py`

The diagnostic sequence was:

CENTER → LEFT → CENTER → RIGHT → CENTER

Each block lasted approximately 5 seconds.

The background gaze worker recorded:

- software acquisition timestamp
- frame number
- face detection status
- left iris ratio
- right iris ratio
- average iris ratio

Stimulus onset events were timestamped using PsychoPy `callOnFlip()` and the same experiment clock.

Development recording:

- Gaze samples: 809
- Stimulus events: 5
- Face detection: 100%

Files:

- `synchronized_iris_20260919_124519.csv`
- `synchronized_stimulus_20260919_124519.csv`

---

### Gaze Sampling Timing

Timestamp differences from the synchronized gaze recording were analyzed directly.

Results:

- Samples: 809
- Mean interval: 33.67 ms
- Median interval: 33.45 ms
- Mean-derived sampling rate: 29.70 Hz
- Median-derived sampling rate: 29.90 Hz
- P95 interval: 34.29 ms
- P99 interval: 35.16 ms
- Maximum observed interval: 195.13 ms

The gaze pipeline therefore operated at approximately 30 Hz under normal conditions, with occasional larger sampling gaps.

Timestamp precision must not be interpreted as equivalent to measurement precision. Normal temporal sampling resolution is approximately 33 ms per sample.

---

### Temporal Alignment

Baseline-relative analysis demonstrated directionally consistent changes following synchronized stimulus transitions.

Development recording observations:

- CENTER → LEFT: clear positive transition around 269 ms
- LEFT → CENTER: clear negative transition around 290 ms
- CENTER → RIGHT: clear negative transition around 310 ms
- RIGHT → CENTER: positive return transition beginning around 263–296 ms

These values were treated as observed gaze transitions rather than validated saccadic latencies.

---

### Baseline Characterization

Pre-stimulus baseline windows of 200 ms, 300 ms, and 500 ms were compared.

A 300 ms window was selected as the current development candidate because it provided approximately nine samples at the observed sampling rate while avoiding instability observed in a 500 ms window in one transition.

This parameter remains provisional and is not yet frozen for Experiment 01.

---

### Candidate Movement Detector v0.1

A preliminary movement-onset detector was evaluated using:

- Baseline window: 300 ms
- Baseline estimator: median
- Noise estimator: median absolute deviation (MAD)
- Threshold: 6 MAD in the expected movement direction
- Persistence: 3 consecutive samples

The detector was developed using the first synchronized development recording.

Development result:

- CENTER → LEFT: 269.40 ms
- LEFT → CENTER: 290.22 ms
- CENTER → RIGHT: 309.80 ms
- RIGHT → CENTER: 263.10 ms
- Detected transitions: 4/4

These values are referred to as candidate gaze movement onsets relative to software-recorded stimulus onset, not clinical saccadic latencies.

---

### Independent Repeat Test

The detector parameters were frozen before evaluation on a new recording.

Independent recording used the intended physical experiment setup.

Files:

- `synchronized_iris_20260919_130036.csv`
- `synchronized_stimulus_20260919_130036.csv`

Recording characteristics:

- Gaze samples: 806
- Stimulus events: 5
- Face detection: 100%

Frozen detector results:

- CENTER → LEFT: 258.48 ms — detected
- LEFT → CENTER: 312.41 ms — detected
- CENTER → RIGHT: 299.48 ms — detected
- RIGHT → CENTER: not detected

Overall:

- Detected transitions: 3/4

No detector parameters were changed after observing the independent recording.

---

### Failure Analysis

The missed RIGHT → CENTER transition showed elevated pre-stimulus variability.

Baseline quality comparison:

| Transition | MAD | Full Range | P10–P90 Range |
|---|---:|---:|---:|
| CENTER → LEFT | 0.0011 | 0.0053 | 0.0033 |
| LEFT → CENTER | 0.0015 | 0.0062 | 0.0046 |
| CENTER → RIGHT | 0.0016 | 0.0046 | 0.0041 |
| RIGHT → CENTER | 0.0044 | 0.0251 | 0.0204 |

The missed transition nevertheless showed a sustained positive post-stimulus displacement, reaching approximately +0.0247 relative to the baseline.

Because the baseline MAD was elevated, the normalized response remained below the frozen 6-MAD threshold.

This identified a failure mode of detector v0.1: unstable pre-stimulus baselines can inflate the MAD-based threshold and prevent detection despite a visible sustained gaze transition.

The detector threshold was intentionally not adjusted after this result.

---

### Current Interpretation

Phase 1D.3C demonstrated that:

1. PsychoPy stimulus presentation and MediaPipe gaze processing can coexist in the same Python environment.
2. Serial gaze processing disrupts stimulus timing.
3. A threaded architecture preserves approximately 60 Hz PsychoPy rendering while gaze processing runs independently.
4. Stimulus and gaze data can be recorded using a shared software timebase.
5. The RGB webcam pipeline provides approximately 30 Hz gaze sampling under normal conditions.
6. Directionally consistent gaze transitions can be observed following synchronized stimulus changes.
7. A preliminary baseline-relative movement detector generalized to 3 of 4 transitions in an independent development recording.
8. Baseline stability is an important quality-control variable and should be assessed before interpreting movement onset.

The current detector remains a development prototype and has not been validated for clinical saccadic latency measurement.

---

### Timing Limitations

Stimulus timestamps generated using PsychoPy `callOnFlip()` represent software-level display flip timing and do not establish physical photon onset.

Camera timestamps are currently recorded immediately after `cap.read()` returns and therefore represent software acquisition timestamps rather than exact camera sensor exposure timestamps.

Potential camera buffering and acquisition latency remain unmeasured.

Consequently, current movement-onset values must not be interpreted as clinical-grade saccadic latency measurements.

External timing validation would be required before making stronger absolute-latency claims.

---

### Status

**Phase 1D.3C — Integrated Stimulus–Gaze Timing Pipeline: PRELIMINARY PASS**

The integrated architecture is technically feasible.

Further development should include baseline-quality handling, task-level integration, and additional independent recordings before parameters are frozen for Experiment 01.

## 2026-09-19 — Phase 1D.4: Prosaccade–Gaze Integration

### Objective

Integrate the validated ±10° prosaccade stimulus with the threaded
camera + MediaPipe gaze acquisition architecture and evaluate whether
directionally appropriate gaze responses can be captured across
single and randomized multi-trial recordings.

### Single-Trial RIGHT Prosaccade

A +10° RIGHT prosaccade was recorded using synchronized PsychoPy
stimulus presentation and background gaze acquisition.

The first recording showed the expected negative gaze displacement,
but pre-target iris tracking was unstable.

Per-eye baseline inspection showed:

- LEFT iris MAD: 0.0137
- RIGHT iris MAD: 0.0345
- average iris MAD: 0.0196

The RIGHT-eye estimator was particularly unstable during this trial.
However, face detection remained available, demonstrating that
successful face detection alone is not sufficient as a gaze-quality
indicator.

An independent repeat showed substantially improved baseline
stability:

- LEFT iris MAD: 0.0012
- RIGHT iris MAD: 0.0013
- average iris MAD: 0.0011

The 250–600 ms post-target median displacement was -0.0425,
consistent with the expected RIGHTward response.

The frozen candidate movement detector v0.1 detected a candidate
gaze movement onset at 261.26 ms relative to the software-recorded
target onset.

### Single-Trial LEFT Prosaccade

A -10° LEFT prosaccade was subsequently tested using the same
acquisition architecture.

Baseline stability was good:

- LEFT iris MAD: 0.0010
- RIGHT iris MAD: 0.0009
- average iris MAD: 0.0016

The 250–600 ms post-target median displacement was +0.0346,
consistent with the expected LEFTward response.

Using the unchanged detector parameters, a candidate gaze movement
onset was detected at 405.07 ms.

The persistence requirement prevented isolated early threshold
crossings from being interpreted as sustained movement.

### Randomized 4-Trial Prosaccade Integration

A balanced randomized diagnostic sequence was implemented with:

- 2 LEFT trials
- 2 RIGHT trials
- random seed: 20260918
- target eccentricity: ±10°
- continuous background gaze acquisition

Generated sequence:

1. LEFT
2. RIGHT
3. LEFT
4. RIGHT

The run completed successfully with:

- 363 gaze samples
- 363 face-detected samples
- 100% face detection
- 20 stimulus events

All four trials produced direction-compatible gaze displacement:

- Trial 1 LEFT: +0.0157
- Trial 2 RIGHT: -0.0341
- Trial 3 LEFT: +0.0250
- Trial 4 RIGHT: -0.0349

Direction-compatible trials: 4/4.

### Frozen Detector Across Four Trials

Candidate movement detector v0.1 was applied without parameter
changes:

- baseline window: 300 ms
- threshold: 6 MAD
- persistence: 3 consecutive samples
- LEFT expected direction: +1
- RIGHT expected direction: -1

Results:

- Trial 1 LEFT: 304.38 ms
- Trial 2 RIGHT: 265.54 ms
- Trial 3 LEFT: 227.73 ms
- Trial 4 RIGHT: 257.48 ms

Detected trials: 4/4.

### Interpretation

The development results demonstrate that the current NeuroMirror
pipeline can:

1. present actual ±10° prosaccade stimuli,
2. continuously acquire webcam-based iris signals,
3. preserve trial-specific stimulus timestamps,
4. distinguish LEFT- and RIGHT-compatible gaze displacement,
5. process multiple randomized trials within one continuous
   acquisition session, and
6. apply the frozen candidate movement detector across trials.

The results also demonstrate that trial-level signal quality can vary
substantially. One single-trial recording showed high iris baseline
variability despite successful face detection, while an independent
repeat was stable.

This supports the future introduction of explicit trial-level gaze
quality control before candidate movement-onset estimation.

### Important Timing Limitation

Reported onset values are candidate gaze movement onsets relative to
software-recorded PsychoPy target onset.

They must not yet be interpreted as clinical-grade saccadic latency.

The current system remains limited by approximately 30 Hz webcam
sampling, software acquisition timestamps after `cap.read()`, possible
camera buffering, and software-level display flip timestamps.

### Status

**Phase 1D.4 multi-trial prosaccade–gaze integration: PRELIMINARY PASS.**

## 2026-09-19 — Phase 1D.5: Trial-Level Baseline Quality Characterization

### Objective

Investigate trial-level gaze baseline quality before scaling the
prosaccade experiment to a larger number of trials.

Previous development recordings showed that successful face detection
did not necessarily imply a stable iris-position signal. Therefore,
baseline quality was characterized independently from face detection.

### Baseline QC Characterization

Seven existing prosaccade development trials were analyzed using the
300 ms pre-target baseline window.

Metrics included:

- baseline median,
- median absolute deviation (MAD),
- full range,
- P10–P90 range,
- median absolute frame-to-frame step,
- P90 frame-to-frame step,
- maximum frame-to-frame step.

Six trials showed baseline MAD values between:

0.0011–0.0036

One previous single RIGHT trial showed substantially greater
variability:

MAD = 0.0196

The median MAD across all seven development trials was:

0.0021

The noisy trial was also clearly separated using frame-to-frame
stability metrics.

Its median absolute frame step was:

0.0280

compared with:

0.0012–0.0056

for the remaining development trials.

This indicates that the noisy recording contained substantial
short-term temporal instability rather than only increased overall
dispersion.

### Raw Eye Geometry Diagnostic

A separate 10-second CENTER fixation diagnostic was recorded to
inspect raw MediaPipe eye geometry.

Recording results:

- samples: 289
- face detected: 289
- face detection rate: 100%

Relative eye-width MAD was:

- LEFT: 0.999%
- RIGHT: 0.813%

The eye-width denominator therefore appeared relatively stable during
this diagnostic.

However, normalized iris-position variability remained substantially
larger:

- LEFT iris-ratio MAD: 0.009123
- RIGHT iris-ratio MAD: 0.011206
- average iris-ratio MAD: 0.009749

These results do not establish a single source of tracking noise.
They indicate that substantial residual variability can remain after
normalization by eye width.

### Local Versus Longer-Term Stability

The same 10-second CENTER recording was divided into non-overlapping
300 ms windows to match the baseline duration used by the candidate
movement detector.

Across 32 windows:

- median window MAD: 0.0019
- minimum window MAD: 0.0004
- P90 window MAD: 0.0055
- maximum window MAD: 0.0089

The median local-window MAD was similar to the median observed across
the prosaccade development baselines.

However, the median iris ratio varied across the 10-second recording:

- minimum window median: 0.4339
- maximum window median: 0.4973
- median drift span: 0.0635

This suggests that the signal may be relatively stable over short
local windows while its center can shift over longer periods.

The source of this longer-term change is not yet established and may
include natural eye movement, head movement, landmark estimation
changes, or combinations of these factors.

This observation supports the continued use of a local pre-target
baseline rather than a single session-wide baseline.

### Relationship Between QC Metrics

Across the seven prosaccade development trials:

- Pearson correlation between baseline MAD and median frame step:
  0.997
- Spearman correlation:
  0.750

Because one extreme noisy trial could strongly influence the Pearson
correlation, a sensitivity analysis was performed without that trial.

This exclusion was for analysis only; the original recording was not
discarded.

For the remaining six trials:

- Pearson correlation: 0.848
- Spearman correlation: 0.600

The two metrics therefore appear related in this small development
sample but are not treated as interchangeable.

No inferential statistical claim is made because of the very small
development sample.

### QC v0.1 Design Decision

Trial-level baseline quality characterization will retain multiple
complementary metrics:

- baseline sample count,
- face detection rate,
- baseline median,
- baseline MAD,
- median absolute frame-to-frame step,
- P90 absolute frame-to-frame step.

No numerical PASS/FAIL threshold is defined at this stage.

The metrics will initially be recorded for characterization rather
than used to automatically reject trials.

This avoids defining quality thresholds from the same small
development dataset used to design the QC procedure.

### Status

**Phase 1D.5 baseline quality characterization: PRELIMINARY PASS.**

Trial-level baseline quality metrics are now defined conceptually,
while numerical acceptance/rejection thresholds remain intentionally
unfrozen pending additional independent data.

## 2026-09-19 — Phase 1D.6: Reusable Gaze Processing Pipeline

### Objective

Convert the exploratory gaze-analysis procedures developed during
Phases 1D.3–1D.5 into reusable and independently tested software
components before scaling the prosaccade protocol.

The existing diagnostic scripts were preserved and were not
refactored during this phase.

---

### Reusable Components

Three reusable modules were introduced.

#### `gaze_processing.py`

Responsibilities:

- extract local pre-target gaze baseline samples
- use a 300 ms development baseline window
- exclude samples at or after target onset
- remove invalid signal samples
- calculate baseline median

#### `gaze_quality.py`

Responsibilities:

- characterize local baseline quality
- calculate:
  - sample count
  - baseline median
  - baseline MAD
  - median absolute frame-to-frame step
  - 90th percentile absolute frame-to-frame step

The module performs descriptive quality characterization only.

No numerical PASS/FAIL quality threshold was introduced.

#### `movement_detector.py`

Candidate Movement Detector v0.1 was formalized using the previously
documented development parameters:

- baseline estimator: median
- noise estimator: MAD
- threshold: 6 × MAD
- persistence: 3 consecutive samples
- LEFT expected direction: +1
- RIGHT expected direction: -1

The detector output is defined as a candidate gaze movement onset
relative to software-recorded target onset.

It must not be interpreted as clinical saccadic latency.

---

### Unit Testing

Dedicated unit tests were added for:

- gaze processing
- gaze quality characterization
- candidate movement detection

Results:

- `test_gaze_processing.py`: 5/5 passed
- `test_gaze_quality.py`: 5/5 passed
- `test_movement_detector.py`: 5/5 passed

Total new reusable-pipeline tests:

- 15/15 passed

---

### Historical Real-Data Validation

The reusable pipeline was evaluated against the previously recorded
randomized four-trial prosaccade dataset:

- `prosaccade_4trial_gaze_20260919_142827.csv`
- `prosaccade_4trial_events_20260919_142827.csv`

The new pipeline reproduced the previously documented candidate
movement-onset results:

| Trial | Direction | Historical Result | Reusable Pipeline |
|------:|-----------|------------------:|------------------:|
| 1 | LEFT  | 304.38 ms | 304.38 ms |
| 2 | RIGHT | 265.54 ms | 265.54 ms |
| 3 | LEFT  | 227.73 ms | 227.73 ms |
| 4 | RIGHT | 257.48 ms | 257.48 ms |

Detected trials:

- 4/4

No detector parameters were changed to reproduce these results.

---

### Interpretation

The reusable implementation reproduced the behavior of the earlier
exploratory analysis on real development data while separating:

1. baseline extraction,
2. baseline quality characterization, and
3. candidate movement detection.

This reduces duplication between future task scripts and provides a
tested analysis foundation for scaling the prosaccade protocol.

Quality-control thresholds remain intentionally unfrozen pending
additional independent data.

---

### Status

**Phase 1D.6 reusable gaze processing pipeline: PRELIMINARY PASS.**

The software components are reusable, unit-tested, and reproduce the
historical four-trial development results.

The next development phase will scale this architecture toward the
full prosaccade protocol without changing the frozen detector v0.1
parameters.



## 2026-09-19 — Phase 1E: Full Prosaccade Protocol Integration

### Objective

Scale the previously validated four-trial prosaccade–gaze architecture
to the full 20-trial development protocol while preserving the frozen
Candidate Movement Detector v0.1 parameters.

This phase remained a development validation.

It was not Experiment 01 Day 1 data.

---

### Full Prosaccade Configuration

The integrated protocol used:

- 20 total prosaccade trials
- 10 LEFT trials
- 10 RIGHT trials
- randomized balanced direction sequence
- maximum 3 consecutive trials in the same direction
- random seed: `20260918`
- fixation duration: 1.0 s
- target duration: 1.0 s
- randomized ITI: 1.0–1.5 s
- target eccentricity: approximately ±10° visual angle
- threaded camera + MediaPipe gaze acquisition
- shared experiment clock for gaze and stimulus events

The randomized direction sequence was:

1. RIGHT
2. RIGHT
3. RIGHT
4. LEFT
5. LEFT
6. RIGHT
7. RIGHT
8. LEFT
9. LEFT
10. LEFT
11. RIGHT
12. LEFT
13. RIGHT
14. LEFT
15. RIGHT
16. RIGHT
17. RIGHT
18. LEFT
19. LEFT
20. LEFT

The generated sequence contained:

- LEFT: 10
- RIGHT: 10
- maximum same-direction run: 3
- generation attempts: 4

---

### Randomized ITI Integration

A randomized ITI sequence was generated using the existing
`generate_random_iti_sequence()` utility.

The planned ITI duration was stored in the event log as:

- `planned_iti_s`

This preserved both:

1. the requested randomized ITI, and
2. the software-recorded actual ITI timing.

A four-trial smoke test confirmed that the randomized ITI values were
successfully propagated through the runtime and event logging pipeline.

---

### Initial Full 20-Trial Development Run

The first full 20-trial acquisition completed successfully and produced:

- 20 completed trials
- 1977 gaze samples
- 1977 face-detected samples
- 100% face detection rate
- 100 stimulus events

Files:

- `prosaccade_20trial_gaze_20260919_174928.csv`
- `prosaccade_20trial_events_20260919_174928.csv`

Event integrity was structurally correct.

However, trial-level baseline analysis identified a startup problem.

Trial 1 contained only:

- 1 sample in the 300 ms pre-target baseline window

The first gaze sample occurred only approximately 111 ms before the
first target onset.

Therefore, the existing fixed startup delay did not guarantee that the
camera + MediaPipe acquisition pipeline had begun producing usable
samples before the first trial.

The 300 ms baseline window and detector parameters were not changed in
response to this problem.

---

### Acquisition Readiness Gate

A startup readiness gate was introduced before the first trial.

The gate waits until the background gaze acquisition pipeline has
produced at least:

- 10 gaze samples

with a maximum startup timeout of:

- 10 seconds

This gate is an acquisition-startup criterion only.

It is not a gaze-quality threshold and does not establish that the
collected samples are clinically or analytically valid.

The fixed one-second startup delay was removed.

---

### Readiness-Gate Smoke Validation

A four-trial smoke validation was performed after introducing the
readiness gate.

The runtime reported:

- `Gaze acquisition ready (10 samples collected).`

Results:

- 4 completed trials
- 431 gaze samples
- 431 face-detected samples
- 100% face detection rate
- 20 stimulus events

Files:

- `prosaccade_20trial_gaze_20260919_182938.csv`
- `prosaccade_20trial_events_20260919_182938.csv`

All four trials contained:

- 9 samples in the 300 ms pre-target baseline window

Baseline MAD values were:

| Trial | Direction | N | MAD |
|------:|-----------|--:|----:|
| 1 | LEFT  | 9 | 0.001697 |
| 2 | RIGHT | 9 | 0.002077 |
| 3 | LEFT  | 9 | 0.004289 |
| 4 | RIGHT | 9 | 0.002539 |

The frozen Candidate Movement Detector v0.1 was then applied without
parameter modification.

Results:

| Trial | Direction | Candidate Onset |
|------:|-----------|----------------:|
| 1 | LEFT  | 257.62 ms |
| 2 | RIGHT | 239.06 ms |
| 3 | LEFT  | 304.43 ms |
| 4 | RIGHT | 283.94 ms |

Detected trials:

- 4/4

These values represent candidate gaze movement onset relative to
software-recorded target onset.

They must not be interpreted as clinical saccadic latency.

---

### Full 20-Trial Validation After Readiness Fix

A second full 20-trial development acquisition was performed after the
readiness gate was added.

Files:

- `prosaccade_20trial_gaze_20260919_184134.csv`
- `prosaccade_20trial_events_20260919_184134.csv`

Runtime results:

- status: COMPLETED
- gaze samples: 2020
- face-detected samples: 2020
- face detection rate: 100%
- stimulus events: 100

The acquisition readiness message was observed before Trial 1:

- `Gaze acquisition ready (10 samples collected).`

---

### Baseline Availability and Quality Characterization

All 20 trials contained:

- 9 samples in the 300 ms pre-target baseline window

Therefore:

- minimum baseline sample count: 9
- maximum baseline sample count: 9
- trials with complete expected baseline sampling: 20/20

This resolved the startup baseline-availability problem observed in the
initial full run.

Baseline stability still varied between trials.

Observed baseline MAD ranged from:

- minimum: 0.000635
- maximum: 0.009116

Trial 15 had the largest observed baseline MAD:

- direction: RIGHT
- baseline median: 0.507949
- baseline MAD: 0.009116

No numerical baseline-quality PASS/FAIL threshold was introduced.

Face detection rate alone was not interpreted as evidence of gaze
signal quality.

---

### Frozen Detector Validation

Candidate Movement Detector v0.1 was applied to all 20 trials using the
previously frozen parameters:

- baseline window: 300 ms
- baseline estimator: median
- noise estimator: MAD
- threshold: 6 × MAD
- persistence: 3 consecutive samples
- LEFT expected direction: +1
- RIGHT expected direction: -1

No detector parameters were tuned using this dataset.

Results:

| Trial | Direction | Detection | Candidate Onset |
|------:|-----------|-----------|----------------:|
| 1  | RIGHT | YES | 152.31 ms |
| 2  | RIGHT | YES | 283.50 ms |
| 3  | RIGHT | YES | 314.70 ms |
| 4  | LEFT  | YES | 245.18 ms |
| 5  | LEFT  | YES | 276.09 ms |
| 6  | RIGHT | YES | 89.56 ms |
| 7  | RIGHT | YES | 321.08 ms |
| 8  | LEFT  | YES | 286.50 ms |
| 9  | LEFT  | YES | 314.66 ms |
| 10 | LEFT  | YES | 377.09 ms |
| 11 | RIGHT | YES | 257.78 ms |
| 12 | LEFT  | YES | 171.21 ms |
| 13 | RIGHT | YES | 318.28 ms |
| 14 | LEFT  | YES | 297.21 ms |
| 15 | RIGHT | NO  | — |
| 16 | RIGHT | YES | 324.25 ms |
| 17 | RIGHT | YES | 321.68 ms |
| 18 | LEFT  | YES | 249.70 ms |
| 19 | LEFT  | YES | 448.49 ms |
| 20 | LEFT  | YES | 310.68 ms |

Detected trials:

- 19/20

This result must not be described as 95% accuracy because no
independent eye-tracker ground truth was available.

---

### Trial 15 Investigation

Trial 15 was investigated without modifying the detector.

Results:

- direction: RIGHT
- baseline samples: 9
- baseline median: 0.507949
- baseline MAD: 0.009116
- 6 × MAD threshold: 0.054694
- maximum expected-direction displacement: 0.049036
- threshold crossings: 0

The post-target signal showed a substantial change in the expected
RIGHT direction, but its maximum directed displacement remained below
the frozen 6 × MAD threshold.

Therefore, Candidate Movement Detector v0.1 correctly returned no
candidate onset according to its existing detection rule.

No threshold reduction or post-hoc detector tuning was performed.

The relationship between baseline variability and detector sensitivity
requires additional data before any detector modification is justified.

---

### Event Integrity Validation

The second full development run contained:

- 20 trials
- 100 total stimulus events
- 5 events per trial

Every trial contained the expected event sequence:

1. `fixation_onset`
2. `target_onset`
3. `target_offset`
4. `iti_onset`
5. `iti_offset`

Results:

- event count integrity: PASS
- event order integrity: PASS

---

### Randomized ITI Runtime Validation

Planned ITI values ranged from approximately:

- 1.0548 s to 1.4991 s

Across the 20 trials, actual software-recorded ITIs were consistently
slightly longer than planned.

Observed ITI error:

- mean: +24.65 ms
- minimum: +17.65 ms
- maximum: +32.52 ms

This difference is consistent with frame-quantized stimulus scheduling
and software/runtime overhead.

These measurements represent software-level event timing only.

They do not establish equivalent physical display timing precision.

---

### Interpretation

Phase 1E demonstrated that the threaded stimulus–gaze architecture can
execute the full randomized 20-trial prosaccade development protocol
while preserving synchronized gaze acquisition and structured stimulus
event logging.

The acquisition readiness gate resolved the first-trial baseline
availability problem observed during the initial full run.

The reusable gaze-processing pipeline successfully characterized all
20 local pre-target baselines.

The previously frozen Candidate Movement Detector v0.1 produced
candidate expected-direction gaze movement detections in 19 of 20
trials without parameter tuning.

The single non-detected trial demonstrated an important limitation of
the current MAD-scaled detector when the local baseline is relatively
variable.

The observed candidate onset values remain development measurements
from an RGB webcam and software-recorded stimulus timing.

They must not be interpreted as clinical saccadic latency.

No clinical validity, diagnostic performance, or Alzheimer-related
inference is established by this phase.

---

### Status

**Phase 1E full prosaccade protocol integration: PRELIMINARY PASS.**

Validated at the current development level:

- full 20-trial randomized prosaccade execution
- balanced LEFT/RIGHT trial generation
- randomized ITI integration
- threaded gaze acquisition
- acquisition readiness gate
- complete 300 ms baseline availability across 20/20 trials
- reusable trial-level baseline characterization
- frozen detector validation without post-hoc tuning
- structured event integrity
- software-level randomized ITI timing characterization

Remaining limitations include:

- no independent eye-tracker ground truth
- no clinical interpretation of candidate onset timing
- no frozen numerical gaze-quality rejection threshold
- no calibration procedure integrated yet
- RGB webcam temporal and spatial limitations remain
- detector behavior under variable baseline quality requires further
  independent data

---

## 2026-09-20 — Phase 1F: Vertical Gaze Geometry and Calibration Preparation

### Objective

Phase 1F began the preparation for the Experiment 01 gaze calibration
and validation pipeline.

The immediate objective was not to implement a final 9-point
calibration model.

Instead, this phase investigated whether the existing MediaPipe iris
landmarks could provide a sufficiently stable vertical eye-geometry
signal to support future two-dimensional gaze calibration.

The work progressed through a sequence of increasingly controlled
diagnostics:

1. vertical iris geometry feasibility
2. manual vertical direction testing
3. fixed visual target validation
4. synchronized visual target and gaze acquisition
5. raw vertical signal analysis
6. vertical eye-geometry quality investigation

No calibration coefficients or numerical gaze-quality rejection
thresholds were defined during this phase.

---

### Phase 1F.1A — Vertical Iris Geometry Feasibility

A new diagnostic was created:

`vertical_iris_geometry_check.py`

Candidate landmarks:

- left iris center: 473
- left upper eyelid: 386
- left lower eyelid: 374
- right iris center: 468
- right upper eyelid: 159
- right lower eyelid: 145

The experimental normalized vertical geometry signal was defined as:

`(iris_y - y_min) / (y_max - y_min)`

where `y_min` and `y_max` were derived from the upper and lower eyelid
landmark coordinates.

This signal was treated only as an experimental eye-geometry feature.

It was not interpreted as a calibrated vertical gaze coordinate.

Example runtime values demonstrated that the calculation could be
performed continuously for both eyes.

### Status

**Phase 1F.1A vertical geometry computation: PRELIMINARY PASS.**

This established computational feasibility only.

It did not establish vertical gaze-direction accuracy.

---

### Phase 1F.1B — Controlled Manual Vertical Direction Check

A second diagnostic was created:

`vertical_iris_direction_check.py`

Four manually controlled viewing conditions were recorded:

1. CENTER
2. TOP
3. CENTER_REPEAT
4. BOTTOM

Each condition was recorded for approximately 5 seconds.

Observed median average vertical ratios:

- CENTER: 0.4465
- TOP: 0.4288
- CENTER_REPEAT: 0.4210
- BOTTOM: 0.4180

Although the initial CENTER-to-TOP transition produced a measurable
change, CENTER_REPEAT did not return to the initial CENTER value.

The subsequent CENTER_REPEAT-to-BOTTOM difference was also small.

The two eyes additionally showed different absolute offsets.

Because the visual targets were manually controlled and the repeated
center condition was not stable, no reliable vertical direction
mapping could be established from this test.

### Status

**Phase 1F.1B manual vertical direction discrimination: INCONCLUSIVE.**

The diagnostic was preserved rather than tuned.

---

### Phase 1F.1C — Fixed Visual Target Diagnostic

A PsychoPy-based fixed-target diagnostic was created:

`vertical_visual_target_check.py`

The existing NeuroMirror monitor configuration was used:

- active display width: 28.5 cm
- active display height: 17.8 cm
- viewing distance: 52.5 cm

A ±10° vertical target position was initially considered.

Physical display geometry showed that the vertical half-height of the
active display corresponds to approximately 9.62° from screen center.

Therefore ±10° vertical eccentricity does not physically fit within
the active display area at the locked 52.5 cm viewing distance.

The vertical diagnostic eccentricity was changed to:

- TOP: +8°
- CENTER: 0°
- BOTTOM: -8°

The horizontal Experiment 01 target eccentricity remains ±10°.

The following sequence was visually validated:

1. CENTER_1
2. TOP
3. CENTER_2
4. BOTTOM
5. CENTER_3

All ±8° vertical targets were visibly contained within the display.

### Status

**Phase 1F.1C fixed vertical target geometry: PRELIMINARY PASS.**

The ±8° value is a display-geometry constraint for the current
hardware configuration, not a biological or clinical parameter.

---

### Phase 1F.1D — Synchronized Vertical Visual Target and Gaze Acquisition

A synchronized diagnostic was created:

`vertical_visual_gaze_check.py`

The architecture followed the previously validated threaded design:

- PsychoPy stimulus presentation on the main thread
- OpenCV + MediaPipe acquisition on a background thread
- shared `core.Clock()` timestamp domain
- `callOnFlip` stimulus event timestamps
- camera timestamps recorded immediately after `cap.read()`

The diagnostic used:

- CENTER_1: 0°
- TOP: +8°
- CENTER_2: 0°
- BOTTOM: -8°
- CENTER_3: 0°

Each condition lasted approximately 5 seconds.

An acquisition readiness gate was used before stimulus execution.

A successful recorded run produced:

- 893 gaze samples
- 893 valid face detections
- 100% face detection
- 5 synchronized stimulus events

Raw files:

`vertical_visual_gaze_20260920_052311.csv`

`vertical_visual_events_20260920_052311.csv`

Raw gaze data and stimulus events were preserved without smoothing,
filtering, calibration correction, or outlier removal.

### Status

**Phase 1F.1D synchronized vertical acquisition: PRELIMINARY PASS.**

This status applies to acquisition and synchronization only.

It does not establish vertical gaze accuracy.

---

### Phase 1F.1D — Condition-Level Vertical Signal Analysis

A separate analysis script was created:

`vertical_visual_gaze_analysis.py`

The recorded data were segmented using stimulus onset timestamps.

Observed median average vertical ratios:

- CENTER_1: 0.3998
- TOP: 0.3901
- CENTER_2: 0.3975
- BOTTOM: 0.3951
- CENTER_3: 0.3832

CENTER_1 to TOP showed a change of approximately -0.0097.

TOP to CENTER_2 showed a partial return of approximately +0.0074.

However, CENTER_2 to BOTTOM changed by only approximately -0.0024
and did not produce the expected clearly separable opposite-direction
pattern.

Per-eye analysis also showed disagreement during some conditions.

For example, the CENTER_2-to-BOTTOM transition produced different
changes in the left and right eye signals, which could be obscured by
simple binocular averaging.

### Status

**Vertical direction discrimination from the current normalized
vertical ratio: INCONCLUSIVE.**

No calibration model was fitted from these data.

---

### Phase 1F.1D — Raw Time-Series Inspection

A raw time-series diagnostic was created:

`vertical_visual_gaze_timeseries.py`

The visualization preserved the raw left-eye, right-eye, and averaged
vertical ratios.

No smoothing, filtering, outlier removal, baseline correction, or
calibration transformation was applied.

The raw signal revealed short episodes of extreme left-eye vertical
ratio values.

One episode extended across approximately frames 177–182 and another
across approximately frames 542–545.

The most extreme observed left-eye ratio was approximately:

`-5.4629`

while the simultaneously recorded right-eye signal remained much less
extreme.

Because the existing synchronized dataset did not store the upper and
lower eyelid coordinates or vertical eye aperture, the cause of these
episodes could not be determined from that dataset.

They were therefore not labeled as blinks or automatically rejected.

Possible contributors include eyelid movement, partial eye closure,
landmark instability, head/eye geometry changes, or combinations of
these factors.

This observation motivated a dedicated eye-geometry quality
diagnostic.

---

### Phase 1F.1E — Vertical Eye Geometry Quality Diagnostic

A new diagnostic was created:

`vertical_eye_geometry_quality_check.py`

The purpose was to preserve the raw components used to calculate the
vertical ratio.

For each eye, the diagnostic recorded:

- iris y-coordinate
- upper eyelid y-coordinate
- lower eyelid y-coordinate
- vertical eye aperture
- normalized vertical ratio

No smoothing, filtering, clipping, rejection threshold, or blink
classification was applied.

Two independent approximately 10-second center-viewing recordings were
collected.

Run 1:

`vertical_eye_geometry_quality_20260920_061217.csv`

- 291 samples
- 291 face detections
- 100% face detection

Run 2:

`vertical_eye_geometry_quality_20260920_061404.csv`

- 292 samples
- 292 face detections
- 100% face detection

In both runs, very small left-eye aperture values coincided with some
of the most extreme left-eye normalized vertical ratios.

Examples included:

- Run 1 minimum left aperture: 0.006505
- corresponding extreme left ratio: approximately -0.2203

and:

- Run 2 minimum left aperture: 0.009939
- corresponding extreme left ratio: approximately -0.3227

The right-eye signal showed substantially less extreme behavior during
the same diagnostics.

These observations provide evidence that vertical eye geometry is
relevant to signal-quality assessment.

However, they do not establish that small aperture is the sole cause
of vertical-ratio instability.

---

### Phase 1F.1E — Geometry Distribution Analysis

A separate analysis script was created:

`vertical_eye_geometry_quality_analysis.py`

The aperture distributions differed substantially between the two
independent runs.

Median aperture values:

Run 1:

- LEFT: 0.024549
- RIGHT: 0.025941

Run 2:

- LEFT: 0.040554
- RIGHT: 0.040821

This between-run difference indicates that an absolute aperture
threshold should not be selected from the current limited data.

The lower aperture tail remained more extreme for the left eye in both
runs.

Minimum apertures:

Run 1:

- LEFT: 0.006505
- RIGHT: 0.017693

Run 2:

- LEFT: 0.009939
- RIGHT: 0.020229

---

### Aperture–Ratio Deviation Association

To characterize the relationship across the full recordings, the
absolute deviation of each vertical ratio from its run-specific median
was calculated.

Spearman correlations between aperture and median-centered ratio
deviation were:

Run 1:

- LEFT: rho = +0.0223, p = 0.7053
- RIGHT: rho = -0.2615, p ≈ 6.14e-06

Run 2:

- LEFT: rho = -0.3344, p ≈ 4.63e-09
- RIGHT: rho = -0.4352, p ≈ 6.31e-15

The relationship was therefore not globally consistent across all
eye/run combinations.

In particular, Run 1 LEFT showed essentially no monotonic relationship
across the complete recording despite containing a small number of
extreme low-aperture frames.

This suggests that the observed geometry-quality relationship may
include nonlinear or lower-tail behavior that is not adequately
described by a single whole-run monotonic correlation.

The p-values are treated only as descriptive statistical evidence of
association within these development recordings.

They do not establish causality or population-level inference.

---

### Current Interpretation

Phase 1F established that:

- synchronized vertical stimulus and gaze acquisition is technically
  feasible
- ±8° vertical targets fit the locked physical display geometry
- the current normalized vertical iris ratio does not yet provide
  sufficiently demonstrated TOP/CENTER/BOTTOM discrimination
- left-eye and right-eye vertical signals can behave differently
- 100% face detection does not imply valid vertical gaze geometry
- very small eye apertures can coincide with extreme normalized
  vertical-ratio values
- aperture distributions can shift substantially between independent
  recordings
- eye aperture is a promising quality-control feature but is not
  sufficient by itself to define frame validity

No numerical aperture threshold has been defined.

No frames have been rejected from the raw datasets.

No blink classification has been introduced.

No calibration model has been fitted.

The next analysis should investigate lower-tail aperture behavior
directly before any quality-control rule is proposed.

---

### Status

**Phase 1F vertical gaze/calibration preparation: IN PROGRESS.**

Sub-phase status:

- 1F.1A vertical geometry computation: PRELIMINARY PASS
- 1F.1B manual vertical direction discrimination: INCONCLUSIVE
- 1F.1C fixed vertical target geometry: PRELIMINARY PASS
- 1F.1D synchronized acquisition: PRELIMINARY PASS
- 1F.1D vertical direction discrimination: INCONCLUSIVE
- 1F.1E eye-geometry quality investigation: PRELIMINARY PASS

The final vertical calibration and validation procedure remains
unimplemented.