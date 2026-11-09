# human_male_prototype_v0.1 — approved walk

Approved by the project owner on 9 November 2026: “this is approved as our prototype walk function.”
The matching local Git tag identifies the frozen checkpoint on `human-prototype-01`.

Scope: the underwear-only human and relaxed, unarmed walk, including loose fists,
heel/ball/toe roll, stable knees and connected chest/shoulder/arm motion. This is
walk approval, not sign-off of a gameplay controller, equipment or the full game.
The existing four-second Idle is included as the review baseline; the dedicated
idle, setting-off and stopping work is authorised for v0.2.

R3 lead; R2/R4/R6 reviews performed sequentially by the same agent. See the
[upper-body review](WALK_UPPER_BODY_REVIEW.md) for changes, measured checks,
known limitations and three-view/eight-facing review evidence. Review cameras
remain governed by [Human Model Review](HUMAN_MODEL_REVIEW.md).

## Frozen artifacts and reproduction

- [Editable animation source](../assets/Blender%20Models/Human-Male-Locomotion.blend)
- [Godot export](../prototype/assets/human_locomotion.glb)
- [Generator](../tools/blender/build_locomotion.py)
- [Hashes](../tools/blender/locomotion_previews/v01_manifest.json)
- [Three-view preview](../tools/blender/locomotion_previews/upper_review_views.gif)
- [Viewer and test commands](../prototype/README.md)

The generator runs against `Human-Male-180cm.blend` using Blender 5.2.3 LTS;
Godot target is 4.5.2 stable. Units: metres, Blender Z-up/-Y-forward to Godot
Y-up/+Z-forward. Walk: 1.2 seconds at 60 Hz, intended travel 0.9 m/s; Idle: four
seconds. Source rig has 137 bones and nine shape keys; GLB exports eight skin
influences without morph targets. MPFB asset provenance remains CC0 as recorded
in the earlier asset review. Original model source is preserved.

Existing full Blender export checks, Godot import/pose/viewer checks and GPU
review captures passed for these artifacts, as recorded in the linked review.
No physical-controller, uneven-terrain, fresh-character recreation or equipment
compatibility test is implied. No merge or remote publication is authorised by
this local version checkpoint.

Checkpoint verification on 9 November: Godot editor import, `test_locomotion.gd`
and `test_locomotion_viewer.gd` rerun successfully. Maximum pose-bound error
0.050426 mm; transition floor +0.533 mm; viewer floor +1.668 mm.
