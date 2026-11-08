# Xbox Controller — Core Control Mapping

**Project:** Gauntlands  
**Reference date:** 8 November 2026  
**Design owner:** R1 — Game Design & Systems Designer; reviewers: R2 (Godot), R6 (QA)  
**Status:** User-provided core mapping, recorded for design reference. Hold alternatives and unspecified buttons remain provisional.  
**Platform:** Xbox controller / Xbox button naming  
**Implementation:** Not implemented or playtested as part of this documentation change.

## Control map

| Physical input | Short press / movement | Notes |
| --- | --- | --- |
| **Left stick (LS)** | Move character | Analogue stick magnitude determines gait: light tilt = walk, full tilt = run. No separate run button. |
| **Right stick (RS)** | Target / aim direction | Directional targeting; lock-on behaviour and attack orientation to be detailed separately. |
| **Right stick click (R3 / RS click)** | Toggle target lock | Xbox physical stick click, distinct from moving the stick. |
| **Left bumper (LB)** | Interact | Original sketch: L1. |
| **Left trigger (LT)** | Offensive power | Original sketch: L2. |
| **Right bumper (RB)** | Use item | Original sketch: R1. |
| **Right trigger (RT)** | Utility power | Original sketch: R2. |
| **Y (top face button)** | Block / parry | Xbox layout Y at top. |
| **X (left face button)** | Attack | Xbox layout X at left. |
| **B (right face button)** | Defensive power | Xbox layout B at right. |
| **A (bottom face button)** | Movement power | Xbox layout A at bottom. |
| **D-pad up / down** | Switch weapon | Direction-specific cycle/order to be finalised. |
| **D-pad left / right** | Switch item | Direction-specific cycle/order to be finalised. |

**Important:** The November 2026 hand-drawn reference used LB/LT/RB/RT positions with PlayStation-like L1/L2/R1/R2 shorthand. This document standardises them to **Xbox** naming. The face cluster must remain physically correct: **Y above, X left, B right, A below**. Do not relocate functions to make a symmetric diagram.

## Press and hold model

Each mapped digital input **may** support a hold-triggered alternate function. This is an extension point rather than a promise that every control has two configured actions.

- **Tap/press:** default action in table above.
- **Hold:** alternative, charged, channelled or context-sensitive action, **only where subsequently assigned**. No specific held action is currently approved.
- A future input specification must define per-input threshold(s), whether tap fires on press or release, how cancellation works, accessibility/remapping, and conflicts between short/long activations.
- Inputs should be modelled as actions rather than hard-coded key names; binding metadata should support device, input type, tap/hold duration, context, class and equipment without duplicating gameplay code.
- D-pad directions, triggers and stick-click interactions are candidates for hold behaviour but must be validated for ergonomics. Analogue stick tilt itself is already used for movement speed and aiming, so do not overload it with accidental hold semantics.
- **Unassigned:** Left stick click (L3/LS click), View, Menu, share button and Xbox system button. Do not invent their gameplay assignments. Xbox system button normally belongs to the platform.

## Expected movement and target semantics

1. Left stick magnitude smoothly controls desired movement speed; small deflection walks, large deflection runs, with a deadzone and configurable transition band to be set during implementation.
2. Character locomotion direction follows left stick; the right stick is reserved for aiming/target direction. When locked, movement may strafe relative to target according to the separate combat targeting specification.
3. Clicking the right stick toggles lock. Rules for target selection, loss of target, camera and aim override are **not yet signed off**.
4. D-pad up/down operates the current weapon selection and left/right operates item selection, without opening menus implicitly.
5. Power and action buttons remain distinct from the core movement and targeting sticks.

## Acceptance criteria for later implementation

- [ ] On a physical Xbox controller, each action invokes the mapped function at the **correct** physical button; Y/X/B/A are not swapped.
- [ ] Walking and running respond to analogue stick deflection without needing a sprint button; deadzone and gait transition are tuneable.
- [ ] Right stick can aim without unintentionally locking; click toggles lock without confusing directional stick input.
- [ ] D-pad vertical inputs change weapons and horizontal inputs change items; no axis reversal.
- [ ] Optional hold action for a mapped button, when configured, is distinguishable from tap and does not accidentally fire both unless explicitly specified.
- [ ] Remapping and controller disconnection/reconnection handling are specified before full implementation.
- [ ] Manual Godot input testing on Windows with the actual Xbox controller is recorded by R6; documentation and an illustrative graphic are **not** proof of implementation.

## Source and linked illustration

This reference was transcribed from the project owner's annotated controller sketch (8 November 2026), corrected to Xbox conventions following review. [Editable vector diagram](xbox-controller-control-map.svg). The PNG exported during the design session is a separate presentation image; its repository upload is not implied by this link.

## Scope / source control

Documentation-only design reference on `main`; no GDScript input map, class powers, models, gameplay files, branch creation or merges are authorised by this record. The first human prototype remains restricted to `human-prototype-01` when explicitly created and approved.
