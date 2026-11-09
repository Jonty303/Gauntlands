# human_male_prototype_v0.2 — idle and transitions

Checkpoint accepted for continued prototype work on 9 November 2026, after the owner reviewed the [chest-entry correction](WALK_START_CHEST_REVIEW.md). The historical first-pass measurements below remain labelled as such. Current WalkStart is 0.7 seconds; current evidence is in the chest-entry review. The owner authorised checkpointing this set before work on running.

Status: work in progress, authorised on 9 November 2026. Baseline: local tag
`human_male_prototype_v0.1`, commit `f4579d0`. R3 leads; R2/R4/R6 reviews are
performed sequentially by the same agent. No independent sign-off is implied.

Bounded first slice: preserve Walk exactly; prepare a planted four-second Idle,
a 0.8-second WalkStart, and mirrored 0.8-second WalkStopL/WalkStopR. These
are in-place authored clips with a recorded virtual travel curve. Start joins
Walk at phase zero; stops enter at left/right contact (phase zero/half).
Idle retains breathing and loose fists; feet share the walk's four-degree toe-out.

Acceptance: preserved Walk curves/exported poses, smooth clip endpoints,
no knee snaps, floor penetration within existing 3 mm tolerance, stable planted
contacts and clear arm/body silhouette. Review the whole sequence at normal speed
in isometric, raised three-quarter and top-down, plus eight-facing poses.
Animation feel remains subject to project-owner review. New timings are trial
values, not previously approved gameplay response targets.

Separate versioned Blender and GLB assets keep the v0.1 checkpoint intact.
No armour, clothing, weapons, gameplay controller, retargeting system or merge.
Godot remains 4.5.2 stable; Blender 5.2.3 LTS. Existing rig, materials, axes,
units, 60 Hz sampling and eight skin influences are retained.

## Artifacts and interfaces

- Authoring: [build_transitions.py](../tools/blender/build_transitions.py), loading the frozen v0.1 derivative.
- Editable source: [Human-Male-Locomotion-v0.2.blend](../assets/Blender%20Models/Human-Male-Locomotion-v0.2.blend).
- Export: [human_locomotion_v02.glb](../prototype/assets/human_locomotion_v02.glb).
- Viewer: [locomotion_v02.tscn](../prototype/locomotion_v02.tscn).
- Export validator: [test_transitions.py](../tools/blender/test_transitions.py).
- Runtime validator: [test_transitions.gd](../prototype/tests/test_transitions.gd).

WalkStart transfers weight towards the right support leg, then steps left and
joins Walk phase zero. Its virtual travel is 0.216 m, accelerating from rest to
0.9 m/s. WalkStopL/R enter at the corresponding leading-foot contact and travel
0.324 m while decelerating to rest. The trailing foot closes the stance; both
stop endpoints match Idle. Source clips run from frame 1; export starts at 0.
The 0.8-second transitions have 49 endpoint-inclusive samples at 60 Hz.

The viewer carries elapsed time through clip boundaries. An Idle request during
Walk waits at most one half-cycle (0.6 seconds), then plays the 0.8-second stop.
A changed request during a transition is queued until that transition completes.
This is an animation-review behaviour, not an approved responsive gameplay input
contract. The start currently leads with the left foot only. Equipment-specific
poses and additional start variants remain later work.

Idle retains the four-second breathing/weight-sway baseline and loose fists,
with both feet planted at the Walk stance width and toe-out. It is deliberately
quiet; no random fidgets, equipment poses or idle variation system is added.
The approved Walk remains an exact animation-channel match in the exported GLB.

## Reproduction

Run from the repository root with the installed Blender/Godot executables:

```powershell
blender --background --factory-startup --python-exit-code 1 --python tools/blender/build_transitions.py
blender --background --factory-startup --python-exit-code 1 --python tools/blender/test_transitions.py
godot --headless --editor --path prototype --quit
godot --headless --path prototype --script res://tests/test_transitions.gd
godot --path prototype res://locomotion_v02.tscn -- --record
python tools/blender/encode_transition_preview.py
```

The encoder uses the existing Pillow preview dependency. Raw frames are ignored;
encoded review media, manifests and validation reports are retained. GPU capture
runs the actual viewer sequence at fixed 30 Hz and renders the three established
orthographic cameras plus eight-facing poses. The preview includes both stop
variants. Pose inspection alone does not certify the perceived timing/fluidity.

## Validation — 9 November 2026

Final Blender build and `test_transitions.py` exited 0. The validator sampled
388 authored new-clip frames and 384 intermediate poses; it also compared every
exported Walk animation channel with v0.1. Godot editor import and
`test_transitions.gd` exited 0. The existing v0.1 viewer regression also passed
after extracting the shared viewer-configuration method. The v0.1 import,
pose and viewer tests were rerun before its commit.

| Gate | Observed result |
| --- | --- |
| v0.1 original/derivative/export/generator preservation | SHA-256 matches retained manifest |
| Approved Walk export channels | Exact match; maximum component difference 0 |
| Saved v0.2 source reopened through Blender MCP | 137 bones, nine shape keys, both textures packed |
| New-clip floor minimum, authored and half frames | +1.954 mm |
| Body/cloth and cloth-self intersections; inside cloth vertices | Zero at all authored new-clip frames |
| Hand/core intersections | Zero at all authored new-clip frames |
| Minimum hand/core clearance | 38.344 mm |
| Maximum planted anchor step drift | 0.000874 mm |
| Maximum sampled sole-vertex step drift | 0.218078 mm |
| Maximum knee speed / acceleration within new clips | 4.158110 degrees/frame / 2.092387 degrees/frame squared |
| Largest endpoint surface difference across joins | 0.005062 mm |
| Knee acceleration across joins | Below the existing 2.2 degrees/frame-squared limit |
| Godot/Blender maximum sampled bounds difference | 0.050187 mm |
| Godot runtime transition floor minimum | +2.077 mm |
| Stops at six requested phases | Both stop variants reached Idle |
| Start at four Idle phases; changed intent; pause; large elapsed-time step | Pass |

Limits retain the v0.1 thresholds: -3 mm floor, 5 mm hand clearance, 6 degrees
per frame knee speed, 2.2 degrees per frame squared knee acceleration, 0.1 mm
contact-anchor step and 3 mm sampled skin step. These are sampled diagnostics,
not continuous collision guarantees. The new join-position gate is 0.1 mm;
source/GLB sampling differences remain far below it. No thresholds were relaxed
in response to a failed animation check.

The first-step roll and lift were reduced after checks found floor/clothing
penetration. Its reach correction and terminal knee curve were then smoothed
until both internal and cross-clip knee checks passed. The approved Walk was
never retuned. Existing exporter weight-reduction/texture-sampler warnings remain.

R3 -> R2/R6 handoff: versioned source/export, build manifest, new viewer, authoring
and validation scripts. Technical acceptance: pass for this review slice.
Human feel approval for v0.2 remains pending. Full gameplay/controller, equipment,
terrain, alternate start lead and fresh-character regeneration remain unverified.
No merge, push or v0.2 release tag has been made.

## Review outputs

- [Normal-speed three-view sequence](../tools/blender/locomotion_v02/first_pass_sequence_review.gif)
- [Transition pose sheet](../tools/blender/locomotion_v02/transition_poses.png)
- [Isometric facings](../tools/blender/locomotion_v02/isometric_facings.png)
- [Raised three-quarter facings](../tools/blender/locomotion_v02/three_quarter_facings.png)
- [Top-down facings](../tools/blender/locomotion_v02/top_down_facings.png)
- [Export validation](../tools/blender/locomotion_v02/first_pass_validation.json)
- [Godot validation](../tools/blender/locomotion_v02/first_pass_godot_validation.json)

GPU capture: 774 sequence frames (258 per view) plus 96 facing/clip poses, exit 0.
The encoded sequence is 8.6 seconds at 30 fps. Isometric and raised three-quarter
views expose the foot lift and closing step; top-down emphasises the shoulder/arm
outline and naturally obscures the legs. This first slice does not increase idle
fidgets or turn the quiet standing loop into a performance animation.

Final sampled visual review: transition pose strip and all three eight-facing
sheets inspected. No obvious silhouette/clothing defect was found in those
poses. Cameras match the v0.1 manifest exactly; GIF timing, 870 raw captures,
version/document links, Python syntax and diff whitespace were checked. Normal-
speed feel approval remains with the project owner.
