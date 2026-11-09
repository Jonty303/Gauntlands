# Dummy test 02: idle, walk and run

9 November 2026. R2 lead; same-agent R3/R6 asset and verification work.
Owner approved test 01 walk as perfect. That complete baseline is preserved
in commit 426f7e2 and remains runnable through dummy_walk.tscn.
Test 02 feel approval is pending. Sprint is explicitly excluded.

## Play

F5 now launches [dummy_locomotion.tscn](../../prototype/dummy_locomotion.tscn).
Left stick controls speed; WASD/arrows walk, Shift runs. Release returns to idle.
1/2/3 or right bumper changes camera; P/Start pauses; R resets.
Space runs a nine-second idle/walk/run/walk/idle rehearsal.
The camera choices are isometric, raised 3/4 and top-down.

The existing 18% stick deadzone is retained. After deadzone remapping,
65% input requests the authored 2 m/s walk; full input requests 4 m/s run.
Acceleration is 3 m/s squared and braking 5 m/s squared. A start from rest
retains one 0.8 m walking step before building past walk speed.
These are test tuning values, not approval of a final movement controller.

Walk/run share a normalised stride phase. Their stride lengths are blended
from 1.6 to 2.4 m and cadence follows distance travelled.
Idle blend takes 0.32 s; run weight responds over 0.25 s.
No dedicated start, stop or turn clips were added. Fast heading changes can
pivot planted feet; the crossfade into wider idle is not a foot-lock system.

## Sources and build

Licence and local asset policy remain as recorded in
[test 01](../kevin_walk/README.md#source-and-licence).
No licensed source or GLB is added to Git; owner downloads remain unchanged.

The approved dummy_walk.glb is reused unchanged.
New source clips from Human Basic Motions FREE 2.4:

| Clip | Source | Source frames at 30 fps | Duration | Travel |
| --- | --- | --- | --- | --- |
| Idle | HumanM@Idle01 | 1-82 | 2.7 s | 0 |
| Run | HumanM@Run01_Forward [RM] | 1-19 | 0.6 s | 2.4 m |

Both use the identical 56-bone dummy rig, native source sampling at 60 fps,
metres, Blender -Y forward / Godot +Z forward and eight skin influences.
Final keys close each loop. Maximum source/bake surface differences:
Idle 1.044 mm, Run 0.372 mm. Same-machine repeat exports produced identical
GLB hashes. This is not a fresh-machine recreation test.

From this checkout, after building the original walk:

    blender --background --factory-startup --python tools/kevin_locomotion/build_dummy_clip.py -- "S:/OneDrive/__Github/Human" Idle
    blender --background --factory-startup --python tools/kevin_locomotion/build_dummy_clip.py -- "S:/OneDrive/__Github/Human" Run
    godot --headless --editor --path prototype --quit
    godot --headless --path prototype --script res://tests/test_dummy_locomotion.gd

Actual tested executables: Blender 5.2.3 LTS at
C:/Program Files/Blender Foundation/Blender 5.2/blender.exe; Godot 4.5.2 console at
C:/Users/jonat/AppData/Local/Temp/gauntlands-godot-4.5.2/Godot_v4.5.2-stable_win64_console.exe.

[Idle manifest](idle_build.json) and [run manifest](run_build.json) record
source hashes, ranges, surface checks and output hashes.
Imported animation resources are blended on the approved walk mesh through
an AnimationTree. Actual skinned foot probes correct floor penetration only,
preserving positive flight height. Maximum correction in rehearsal: 35.795 mm.
This changes whole-actor height, not the authored limb rotations.

## Verification and review

[Validation](validation.json) records actual headless and rendered test results:

- Approved walk: zero measured bone-pose difference across 24 phases.
- All three clips have expected lengths; Sprint is absent.
- Nine rehearsal cases: 30/60/120 Hz x three cameras, identical travel and phase.
- Run -> walk -> idle from eight starting stride phases passes.
- Pause preserves position and phase.
- Sampled full skin floor clearance stays at least 0.49999 mm.
- Maximum sampled knee rotation step at 60 Hz: 15.012 degrees.
  The test guard is 25 degrees; this is a discontinuity guard, not artistic approval.
- Same-machine repeat Idle and Run exports match their respective manifests.
- Godot editor/import passes. Physical joypad testing remains unverified.

Capture command: run the same test without --headless, followed by -- --capture.
Package with python tools/kevin_locomotion/package_previews.py and Pillow.
Three nine-second sequences and 48 idle/run facing poses cover the review views.
[Preview manifest](preview_manifest.json) records frame counts and durations.
Visual review findings are appended after inspecting the generated sheets.

## Lessons and failed checks

The supplied idle needs its constraint state primed after selecting the action:
evaluate the loop end and beginning before collecting samples. Without this,
the first sampled pose was stale and closure/preservation failed by 0.891 m.
Priming resolved that failure; the remaining endpoint difference is 1.044 mm.
The publisher's original hand-control dependency warnings remain, but the baked
rig has no constraints and repeat export checks match.

An initial capture after rebuilding failed because rewriting import metadata
replaced Godot's generated cache path. The new builder retains existing import
metadata, and the documented editor/import step is required after builds.
Reimport restored the cache; subsequent checks passed.

The copied review UI initially inherited incorrectly decoded UTF-8 text and
old walk-only help. The new script now uses explicit UTF-8 and corrected controls.
The approved walk scene and asset were not modified.

## Rendered review completed

Inspected all three transition-sequence sheets and all three idle/run facing
sheets (48 facing poses). The dummy stays complete and readable in each view;
idle has the supplied wider staggered stance, run has a distinct bent-arm swing,
and the sampled run-to-walk sequence returns to the accepted walk pose.
No obvious explosive deformation was visible in these samples. Temporal feel
and the simple stop crossfade remain for owner review at normal playback speed.

## Owner acceptance

The owner approved this idle/walk/run test as excellent, then accepted the broader
resource-evaluation milestone on 9 November 2026. [Checkpoint](../../development/PROTOTYPE_02_CHECKPOINT.md).
Earlier pending temporal-feel notes above describe the pre-review state.
