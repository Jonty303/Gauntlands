# Motion demo v0.4 — implementation brief and evidence

9 November 2026. R2 lead; R3 animation interface and R6 validation reviewed by
one agent. User authorised the bounded demo with “please proceed”. Baseline:
905160c, accepted v0.3 animation asset at 5161379. Human feel sign-off is pending.

Current runtime follow-up: [run-up polish](RUN_UP_REVIEW.md). It supersedes the
initial full-stick acceleration timing and Replay test sequence described below.
Original results/previews remain historical evidence for the first demo pass.

## Scope and interface

Separate playable scene on human-prototype-01 in Jonty303/Gauntlands; no changes
to the archive/2D reboot, Blender assets or accepted review viewers. A flat metre
grid, one character, camera-relative analogue movement, smooth steering and
speed, walk/run animation, three review angles, controls and telemetry. No combat,
equipment, levels, new turn clips, IK or full animation framework.

[Controller baseline](../encyclopedia/design%20reference/xbox-controller-controls.md):
left stick controls direction and magnitude. No controller sprint button. WASD
and arrows walk; Shift provides keyboard-only full-tilt equivalent. Review UI
uses mouse and 1/2/3, P pauses, R resets. Reserved gameplay buttons stay unassigned.

Simulation uses metres, Godot Y up, character +Z forward. Keep intent, speed and
heading separate from the animation adapter. Movement uses a circular 0.18 input
deadzone; the remaining magnitude maps continuously to 0–2.2 m/s, with 0.9 m/s at
55% effective tilt. Initial tuning: acceleration 3.2 m/s², braking 5.5 m/s²,
heading speed 420°/s walking to 210°/s running, eased angular acceleration.
Sharp turns reduce speed; no instantaneous facing changes. These are this pass's
provisional tuning values, not previously approved game rules.

Animation reuses v0.3 Idle, WalkStart, Walk, Run and WalkStopL/R. Loop changes keep
normalised foot phase and blend; playback follows travelled speed. Starts/stops
can be interrupted by the latest intent. The authored one-second gait bridges
remain in the review viewer; gameplay must not queue whole clips before responding.
A direct run stop and planted turns are not supplied by v0.3; runtime blending
is a provisional approximation and requires explicit visual review.

Camera azimuth/elevation match the accepted isometric, raised 3/4 and top-down
presets; the demo follows position at fixed orientation. Gameplay framing is
wider than the 2.8 m model inspection view. A close framing toggle enables review.

## Acceptance and validation plan (set before implementation)

- Deadzone drift produces zero movement; full input never exceeds 2.2 m/s;
  diagonal input is not faster. All eight headings and arbitrary stick angles work.
- Changed input affects speed/steering on the next simulation tick; no queued
  gait bridge. Release reaches rest within 0.5 s from maximum speed.
- No instant yaw jump; run turns wider than walk. 180° reversal slows before
  travelling in the new direction. Focus loss/disconnect cannot leave stuck input.
- Test 30/60/120 Hz scenario results, with fixed internal substeps; position
  disagreement target <2 cm. Animation endpoints and bones remain finite.
- Preserve accepted manifests and review viewer tests. Run Godot headless import
  plus the new motion suite. Capture all three views with the same scripted input.
- Review actual rendered poses/motion separately from automated results. Physical
  gamepad feel, sharp-turn foot pivot and arbitrary-phase stop blends must remain
  unverified until tested; do not equate synthetic input with physical testing.

## Implementation and use

F5 now opens [motion_demo.tscn](../prototype/motion_demo.tscn). Its script builds
only this test stage. [Motion state](../prototype/motion/motion_state.gd) owns
speed/heading/position; [input](../prototype/motion/motion_input.gd) owns actions,
deadzone and focus/disconnect protection; [animation](../prototype/motion/motion_animation.gd)
owns a manually advanced AnimationTree with synchronised Walk/Run phase and
interruptible Start/Stop/Idle layers. The initial 0.1 s weight transfer is retained.
Cycle lengths are 1.08 m walking and 1.76 m running; mixed stride length determines
phase from actual travel. Nominal start speed is capped by a smooth 0.1–0.7 s
ramp. This is a gameplay approximation, not exact replay of authored virtual travel.

Input uses Godot actions. Effective tilt is remapped after the circular deadzone.
Keyboard diagonal is normalised; Shift affects keyboard only. Disconnection or
loss of focus clears actions and requires neutral before resuming. P pauses
simulation/animation; R resets while preserving the chosen view and pause state.
Replay test runs the same 11.2 s scenario; live movement cancels replay. A frame
longer than 0.25 s discards excess simulation time rather than causing a large jump.
There is no collision/navigation system in this deliberately flat test scene.

The camera follows position with fixed orientation. 1/2/3 select isometric,
raised 3/4 and top-down; normal framing is 6.5 m, Close view is the original 2.8 m.
The existing [v0.3 viewer](../prototype/locomotion_v03.tscn) remains available with F6.

## Failed trial and verified correction

First runtime blends dipped the sampled sole 8.665 mm below the plane, although
all individual clips passed their original checks. Added a root-only vertical
clearance correction from exported, weighted foot vertices; no joint rotations
or source assets are changed. For this model, 2,220 probes have rest mesh Y <45 mm
and foot/toe influence >0.15. The maximum correction in the rehearsal is 9.961 mm.
Correction releases exponentially at 18/s and never smooths below the floor.
This is model-specific floor protection, not IK or a claim of planted X/Z feet.
A first all-foot selection used 2,529 probes; narrowing to sole vertices reduced
work and passed the same full-body skin checks. A very short cancelled start now
settles without inventing a complete stop step.

## Validation executed — 9 November 2026

Godot executable used:
`C:/Users/jonat/AppData/Local/Temp/gauntlands-godot-4.5.2/Godot_v4.5.2-stable_win64_console.exe`.
Run from the Gauntlands repository, substituting the installed executable for godot:

```powershell
godot --headless --editor --path prototype --quit
godot --headless --path prototype --script res://tests/test_motion_demo.gd
godot --headless --path prototype --script res://tests/test_run.gd
godot --path prototype -- --motion-capture
python tools/motion_v04/package_previews.py
```

Preview packaging requires Pillow; this installation used the existing
`$env:TEMP/gauntlands-preview-libs` via PYTHONPATH. No new dependency installed.

- Import/parser: pass, exit 0 after final code changes.
- [Motion suite](../prototype/tests/test_motion_demo.gd): pass, exit 0.
  [Machine-readable results](../tools/motion_v04/validation.json).
- Identical rehearsal path at 30/60/120 Hz; 24 direction/camera cases agree within
  0.0000005 m. Maximum speed 2.2 m/s; all full-speed releases stop within 0.5 s
  and 0.5 m. Sixteen arbitrary-phase stops (eight per gait) settle and pass floor checks.
- Changed intent, start cancellation, restart, pause, keyboard diagonal/run mapping,
  synthetic radial deadzone and focus/disconnect suppression: pass.
- All sampled bones finite. Maximum 60 Hz heading step 6.992 degrees, bounded by
  the 420 degrees/s turn limit. Largest measured bone step is 8.107 degrees on
  lowerarm01.L during the run stop; this is a diagnostic, not an accepted quality limit.
- Full-body skin bounds every six frames at 60 Hz through the rehearsal, plus
  arbitrary-phase stop samples: lowest height -0.000000133 m (float noise).
  The added runtime floor gate was set to -3 mm before the first clearance check;
  the initial failure above was fixed, not hidden by relaxing it.
- Existing v0.3 regression: pass, exit 0; maximum imported bounds discrepancy
  0.050306 mm. Accepted v0.1/v0.2/v0.3 manifest hashes checked separately.
- Rendered 336 frames per view (1,008 PNGs); capture error log empty. Packaged three
  112-frame / 11.2 s GIFs; frame counts/durations verified. Raw frames are ignored.
- Agent inspected sampled starts, gait changes, turns and stops in all three
  contact sheets. Live UI inspection verified XInput detection, Replay test and
  camera switching. This is sampled visual review, not owner feel approval.
- Physical joypad movement, unplugging hardware and normal-speed owner review:
  **not performed by the agent**. Headless Godot sees no pad; the rendered Windows
  session reports an XInput Controller. No physical-controller test is claimed.

## Review artifacts and handoff

[Isometric](../tools/motion_v04/isometric.gif),
[raised 3/4](../tools/motion_v04/three_quarter.gif),
[top-down](../tools/motion_v04/top_down.gif).
Contact sheets: [isometric](../tools/motion_v04/isometric_poses.png),
[3/4](../tools/motion_v04/three_quarter_poses.png),
[top-down](../tools/motion_v04/top_down_poses.png).
[Reproducible packaging](../tools/motion_v04/package_previews.py).

R2 -> R3/R6 same-agent review: simulation/asset interfaces accepted for this demo;
headless and sampled render gates pass. Source provenance is the existing accepted
v0.3 GLB; no generated or externally sourced art was added. R6 -> owner: ready for
interactive feel review, not signed off as final locomotion. No v0.4 release tag,
merge or push is authorised by this handoff.

Residual risks: sharp turns rotate the whole body and may pivot/slide planted feet;
very low tilt retimes a full-length walk rather than shortening its stride; the
run stop blends to the nearest existing walk-stop lead and may need a dedicated
clip. No runtime clothing/self-collision guarantee follows from the old source
clip tests. Performance has not been profiled against a production budget. Use
Close view and Replay test to assess these before approving the next animation pass.

Implementation reference: Godot 4.5 [AnimationTree](https://docs.godotengine.org/en/4.5/classes/class_animationnodeblendtree.html)
and [controller input](https://docs.godotengine.org/en/4.5/tutorials/inputs/controllers_gamepads_joysticks.html).


## Owner observation during demo handoff

The owner asked whether moving foot placement should come slightly inward, while
Idle uses a wider or lightly staggered stance. Source inspection confirms the same
nominal lateral ankle targets (+/-0.125 m) in build_locomotion.py (Idle and Walk),
build_transitions.py and build_run.py, before rocker/yaw offsets. That is nominal
ankle-target spacing, not a measured sole-centre spacing in every rendered pose.

Proposed next animation pass: modestly narrower moving foot tracks, separately
adjustable walk/run/idle widths, and a subtle stagger at rest. Move each landing
inward during swing, maintain planted contacts, and establish the resting stance
through stopping steps. Retest knee tracking, pelvis balance, garment clearance,
all transition joins and all three demo views. Do not toe-in the feet merely to
reduce width, cross the centreline by default, or slide planted feet laterally.
This is a recorded candidate based on the owner's observation; source clips were
not changed in this demo implementation and the new widths are not yet approved.
