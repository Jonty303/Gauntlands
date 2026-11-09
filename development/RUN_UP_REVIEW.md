# Run-up polish — motion demo v0.4

9 November 2026. User requested a clear walking lead-up before running.
R2 lead, R3/R6 same-agent animation/interface review. Baseline 69e9ea7;
accepted source remains v0.3 at 5161379. Scope: runtime run-up timing only.
Stance width remains the separately recorded next candidate.

## Contract before implementation

From rest: retain the authored 0.7 s weight-transfer start, complete one 0.54 m
travelling walk step at no more than 0.9 m/s, then ease the speed ceiling from
0.9 to 2.2 m/s over 0.55 s. The existing 3.2 m/s² acceleration bound still applies.
Count actual travel, not elapsed waiting, to keep the step meaningful at partial
stick and while turning. Walk/Run phase and cadence remain driven by travel.
An established walk must not restart or reset its phase when run is requested.
Release, direction changes and pause remain immediate simulation intents, with
existing braking and steering limits. No forced completion of a queued animation.

Acceptance: no Run weight before the travelling walk step; run speed reached
within 2.1 s of a straight full-tilt start; 30/60/120 Hz results agree within
2 cm; first-step completion and ramp timing agree within one sampling frame.
Release during each stage must brake on the next tick and stop within 0.5 s.
Reversal during the lead-up must steer on the next tick. Existing motion suite
and import must pass. Sample actual rendered motion in the three review views.
Physical-controller feel and owner sign-off remain separate from automated checks.

## Evidence

Implemented in [motion_state.gd](../prototype/motion/motion_state.gd): new
first_step_remaining and run_build_time fields reset on a genuine start from rest.
The animation adapter reports Walk lead-in during that step; its phase/pose
sampling is unchanged. [Replay test](../prototype/motion_demo.gd) now begins with
full tilt from idle, then returns to walk before its existing turn/reversal checks.

Commands executed with installed Godot 4.5.2 stable, from the repository root:

```powershell
godot --headless --path prototype --script res://tests/test_run_up.gd
godot --headless --path prototype --script res://tests/test_motion_demo.gd
godot --headless --editor --path prototype --quit
godot --path prototype --script res://tests/test_run_up.gd -- --run-up-capture
python tools/motion_v04/run_up/package_previews.py
```

Executable used: `C:/Users/jonat/AppData/Local/Temp/gauntlands-godot-4.5.2/Godot_v4.5.2-stable_win64_console.exe`.
Pillow used the existing `$env:TEMP/gauntlands-preview-libs` PYTHONPATH.
The initial test script had an inferred-type parser error for its frame time;
explicit float typing corrected it. Final import and both suites exit 0.

[Run-up results](../tools/motion_v04/run_up/validation.json):

| Measurement | Observed |
| --- | --- |
| First travelling walk step complete | 1.30 s after full input |
| Walk phase at completion sample | 0.50694 (opposite foot contact) |
| First measurable Run blend | 1.425–1.433 s |
| Full 2.2 m/s speed | 1.85–1.867 s |
| Travel after 3 s | 4.1867765 m, identical at 30/60/120 Hz |
| Lowest sampled skinned sole | -0.000000177 m (float noise) |
| Release tests | All five stages brake immediately and stop within 0.5 s |
| Restart / steering / established walk / pause | Pass |

[Full motion regression](../tools/motion_v04/run_up/motion_validation.json): pass,
16 arbitrary-phase stops and 24 direction/camera cases, identical three-rate
rehearsal path, largest sampled 60 Hz bone step 7.79 degrees. The existing vertical
clearance correction peaks at 28.52 mm in the revised rehearsal; it still prevents
floor penetration but remains a runtime approximation to inspect for visible bob.
The original v0.4 report is preserved; it describes the earlier rehearsal.

Captured 126 frames per view at 30 Hz, error log empty. Packaged previews have
63 frames and 4.2 s duration each (15 fps with GIF timing quantisation). Agent
inspected start, completed walking step, run build and stop poses in all three
views. Normal-speed physical-controller feel and owner acceptance are pending.
No Blender source, export or frozen generator was modified; accepted v0.1/v0.2/
v0.3 manifests are checked before handoff. The archived run viewer was not changed
and its expensive mesh regression was not repeated in this runtime-only pass.

## Review artifacts and handoff

[Isometric preview](../tools/motion_v04/run_up/isometric.gif) ·
[3/4 preview](../tools/motion_v04/run_up/three_quarter.gif) ·
[top-down preview](../tools/motion_v04/run_up/top_down.gif).
[Isometric poses](../tools/motion_v04/run_up/isometric_poses.png) ·
[3/4 poses](../tools/motion_v04/run_up/three_quarter_poses.png) ·
[top-down poses](../tools/motion_v04/run_up/top_down_poses.png).
[Capture/validation script](../prototype/tests/test_run_up.gd),
[packaging](../tools/motion_v04/run_up/package_previews.py).

R2 -> R3/R6 same-agent review: timing, interruption and source-preservation gates
pass; sampled three-view poses inspected. Next owner is the user for feel review.
This is a development checkpoint, not an approved new animation-source version.
Remaining limitations from the motion demo persist: sharp-turn foot pivoting,
low-speed stride retiming and direct run-stop blend quality. Stance width is the
next separately recorded polish candidate. No merge, release tag or push performed.
