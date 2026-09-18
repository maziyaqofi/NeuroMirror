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