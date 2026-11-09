# Idle/walk animation handoff — 8 November 2026

## Scope and ownership

User requested idle and walking animations following the accepted 1.80 m test
model and successful animated export proof. R3 lead; R2 integration and R6 QA
performed sequentially by the same agent, with R5 reproducibility checks.
Existing `human-prototype-01` only. This delivers two reviewable clips and their
review-player transitions; it does not implement gamepad movement, aiming,
combat, new clothing, retargeting or the complete first gameplay milestone.

## Artifacts and interface

- [Human-Male-Locomotion.blend](../assets/Blender%20Models/Human-Male-Locomotion.blend):
  separate editable derivative, existing 137-bone rig and nine shape keys, packed
  skin/eye images, Idle and Walk actions. Original and accepted model preserved.
- [human_locomotion.glb](../prototype/assets/human_locomotion.glb): baked body
  shape and modifiers; both animation clips; up to eight skin influences.
- [Godot review scene](../prototype/locomotion.tscn): now the default F5 scene.
  Shared review presentation is configurable in `proof.gd`; the original
  diagnostic remains intact in `proof.tscn` and passes its regression test.
- [Authoring script](../tools/blender/build_locomotion.py),
  [export validation](../tools/blender/test_locomotion.py),
  [engine validation](../prototype/tests/test_locomotion.gd),
  [viewer transition tests](../prototype/tests/test_locomotion_viewer.gd).

| Contract | Value |
| --- | --- |
| Units and axes | Metres; Blender Z-up/-Y-forward; Godot Y-up/+Z-facing |
| Idle | 4 seconds; frames 1–241 at 60 fps; relaxed arms, small torso/sway motion |
| Walk | 1.2 seconds; frames 1–73 at 60 fps; in place, no forward root travel |
| Reference travel | 0.9 m/s; 1.08 m per complete cycle, 0.54 m per step |
| Foot stance | 60% of each leg's cycle; opposite leg offset half a cycle |
| Swing | Smooth forward trajectory, up to 95 mm ankle lift |
| Ground placement | Nominal sole clearance 3 mm; flat stance feet |
| Looping | Both action endpoints match; viewer loops both clips |
| Import/export | Timeline shifted to zero; 60 fps import, no lossy animation optimisation or mesh compression |

The builder solves leg positions analytically using the existing thigh/shin
lengths and adjusts pelvis height to avoid knee overextension. It bakes normal
bone keyframes, not a new runtime IK framework. Relaxed arms swing opposite to
the advancing leg. Feet remain horizontal: heel-strike/toe-off articulation is
not claimed as finished. The gait is a foundation for human visual review.

The new derivative adds ten local weight-smoothing passes to the briefs' narrow
crotch region. This resolved a real inner/outer shell crossing at one stride
frame. It changes neither garment topology nor the accepted source model. Other
export limitations from the diagnostic still apply: cloth smoothing/thickness
are baked, morphs remain editable only in Blender, and weights above eight are
reduced by the exporter. The resulting exported geometry is what was tested.

## Transition behaviour

The reviewer starts Walk at its passing pose (0.36 s), with a 0.10 s blend.
An Idle request while walking waits for the next passing pose (0.36 or 0.96 s),
then blends for 0.10 s. Maximum stop wait is one half-cycle, about 0.6 s. Paused
selection changes clips immediately. This is a deliberate review-player policy;
responsive gamepad starts/stops and motion matching need their own next-step tests.

A plain arbitrary 0.25 s cross-fade caused about 11.8 mm floor penetration and
was rejected. The recorded passing-pose blends stay within the task's 3 mm floor
settling tolerance. The isolated blend test observed -1.228 mm; tests of the
actual viewer selector observed -0.017 mm. This is not a claim of mathematically
zero floor penetration during every blend, nor foot locking on uneven terrain.

## Evidence

[Build manifest](../tools/blender/locomotion_previews/build.json) ·
[Blender exported-clip validation](../tools/blender/locomotion_previews/validation.json) ·
[Godot comparison](../tools/blender/locomotion_previews/godot_validation.json) ·
[Viewer behaviour](../tools/blender/locomotion_previews/viewer_validation.json).

| Check | Observed outcome |
| --- | --- |
| Saved derivative reopened | Pass: Idle/Walk actions, 9 shape keys, packed used textures |
| Accepted source preserved | Pass: SHA remains `a4bd547d659e928b132f530f166d96fd20e9001fedb09dcc424e7c65c0fc1d75` |
| Exported idle | Pass: all 241 integer frames, zero body/self intersections or inside-cloth vertices |
| Exported walk | Pass: all 73 integer frames, zero body/self intersections or inside-cloth vertices |
| Minimum cloth clearance | Idle 4.428 mm; Walk 2.919 mm |
| Loop seams | Pass: zero measured vertex difference between first/last poses for both clips |
| Stance speed | Pass: exported foot-bone step error below 0.000001 m relative to 0.9 m/s virtual travel |
| Ground clearance in loops | Pass: minimum skin height about 2.995 mm; no loop-frame ground penetration |
| Godot import/poses | Pass: 137 bones, expected clip durations, 10 sampled poses across both clips; maximum bounds error 0.049711 mm against independently evaluated Blender GLB |
| Blend tests | Pass within 3 mm floor tolerance; exact residuals above |
| Actual viewer stop logic | Pass: stop requests at 0, 0.2, 0.6, 1.05 s complete within one step; paused selection also tested |
| Diagnostic regression | Pass: original engine comparison remains at 0.050307 mm maximum bounds error |
| GPU rendering | Six actual Godot captures plus a 36-frame walk GIF; poses inspected from three-quarter, side and back |
| Human motion/artistic acceptance | Pending user review; no physical gamepad testing performed |

Tests cover the authored 60 Hz frames, not every possible interpolation between
frames. Foot-speed measurement uses the foot bone, not optical tracking of every
sole vertex. Engine checks compare reconstructed skinned bounds, not every mesh
vertex. Self-intersection adjacency accounts for glTF UV/material seam splits,
including geometric coincidences within 0.001 mm. No performance budget is
certified, and no walk/run/turn blending is implemented.

## Reproduction

Blender 5.2.3 LTS `e13b728c6880`; Godot 4.5.2 stable `6ce3de25a`.
Use the same executable paths recorded in the diagnostic handoff. From repo root:

```powershell
$blenderExe = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$godotExe = "$env:TEMP\gauntlands-godot-4.5.2\Godot_v4.5.2-stable_win64_console.exe"
& $blenderExe --background --factory-startup 'assets/Blender Models/Human-Male-180cm.blend' --python-exit-code 1 --python tools/blender/build_locomotion.py
& $blenderExe --background --factory-startup --python-exit-code 1 --python tools/blender/test_locomotion.py
& $godotExe --headless --editor --path prototype --quit
& $godotExe --headless --path prototype --script res://tests/test_locomotion.gd
& $godotExe --headless --path prototype --script res://tests/test_locomotion_viewer.gd
& $godotExe --headless --path prototype --script res://tests/test_import.gd
& $godotExe --path prototype -- --capture
& $godotExe --path prototype -- --record
```

All operations above ran. GPU captures were launched using hidden background
processes with logs. The generator overwrites only its generated locomotion
outputs; preserve manual changes to those before rebuilding. Blender validation
must precede the Godot comparison, which checks the GLB hash against its reference.
An optional quick validation uses `-- --quick`; that was used during development,
but the delivered report is the full run (`quick: false`).

The optional GIF encoder uses Pillow installed into a temporary directory, not
project/runtime dependencies. It converts 36 actual engine frames to a looping
1.2 s preview at 660 x 540. PNG captures remain the higher-resolution evidence.
Assets inherit the CC0 MPFB skin/eye provenance documented in
[the diagnostic handoff](ANIMATION_PROOF_REVIEW.md); animation and briefs are
project-authored. No motion-capture downloads or external animation service used.

## Next handoff

R3 -> R2/R6: use these two clips at the specified cadence and reference speed.
Next implement gamepad travel and facing, matching movement speed to playback,
then test starting/stopping, diagonal speed, turns and controller behaviour on
the flat plane. That will complete the first major milestone after user review.

[Idle](../tools/blender/locomotion_previews/idle.png) ·
[Contact](../tools/blender/locomotion_previews/walk_contact.png) ·
[Passing](../tools/blender/locomotion_previews/walk_passing.png) ·
[Side](../tools/blender/locomotion_previews/walk_side.png) ·
[Back](../tools/blender/locomotion_previews/walk_back.png) ·
[Animated walk](../tools/blender/locomotion_previews/walk.gif).
