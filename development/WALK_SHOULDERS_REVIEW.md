# Shoulder follow-through pass - 8 November 2026

Historical pass: followed by the [landing and supported-rise pass](WALK_LANDING_REVIEW.md). Shared reports and current walk previews now describe the later pass.

## Scope and handoff

User requested a restrained increase in shoulder movement. R3 leads, with R2/R6
integration and validation performed sequentially by the same agent. Existing
`human-prototype-01`, Jonty303/Gauntlands only. Artistic acceptance is pending;
no commit, push, branch or merge.

Target: a little more chest/shoulder motion and delayed arm follow-through,
without a conspicuous shrug, new clipping or changes to the current footwork.
The preceding pass is saved at
`%TEMP%/gauntlands-shoulders-before-20261108-232907`.

## Changes

The [generator](../tools/blender/build_locomotion.py) now exposes the upper-body
settings as named parameters and records them in
[build.json](../tools/blender/locomotion_previews/build.json):

| Setting | Before | This pass |
| --- | --- | --- |
| Chest counter-yaw amplitude | 2 degrees | 3.2 degrees |
| Chest delay | None | 0.015 cycle / 18 ms |
| Added clavicle yaw amplitude | 1 degree | 1.4 degrees |
| Added clavicle bank amplitude | None | 0.7 degree, alternating sides |
| Clavicle delay | None | 0.030 cycle / 36 ms |
| Upper arm / forearm / wrist phase delays | 0.025 / 0.045 / 0.065 cycle | 0.045 / 0.065 / 0.085 cycle |

Counter-yaw is distributed through the five spine segments. The clavicles follow
with a small delay and alternating rise/fall. Arm swing amplitude, elbow flex,
wrist amplitude and loose fists retain their prior settings; their timing follows
the new shoulder motion. The head retains its prior orientation counter-motion.

R3 -> R2/R6 artifacts: [editable derivative](../assets/Blender%20Models/Human-Male-Locomotion.blend),
[GLB](../prototype/assets/human_locomotion.glb), generator, refreshed
[pose bounds](../prototype/tests/locomotion_bounds.json), build/validation reports
and GPU previews. Validation and viewer code were not changed in this pass.

Interfaces remain: metres; Blender Z-up/-Y-forward and Godot Y-up/+Z-facing;
137 bones, nine source shape keys, packed textures, clothing, 8-influence export;
60 Hz bake, 4-second Idle, 1.2-second Walk, 0.9 m/s reference speed, 60% stance,
half-cycle leg offset and existing viewer transition rules. Sprite dimensions and
gameplay events are not applicable. Original source model hash preserved.

## Evidence

Blender 5.2.3 LTS and Godot 4.5.2 stable. The build and full Blender validator
exited 0, with 241 Idle frames, 73 Walk frames and 72 intermediate floor samples.
A separate source comparison sampled root, both hips/knees/feet/toes at all
73 Walk frames: all matrix elements match the previous pass exactly.

| Check | Result |
| --- | --- |
| Shoulder-line yaw excursion | 5.780 -> 8.879 degrees total range |
| Left-minus-right shoulder-height excursion | 13.890 -> 22.446 mm total range; not per-shoulder lift |
| Lower-body source pose matrices | Zero difference at all sampled frames |
| Original source / save-reopen / shape keys | Pass; original preserved, nine keys |
| Loop endpoint vertex difference | Zero |
| Hand self / body-cloth / cloth self / inside-vertex checks | Zero across authored frames |
| Hand-thigh clearance | 15.792 mm minimum, zero intersections |
| Elbow range / maximum 60 Hz change | 15.828-26.439 degrees / 0.492 degree |
| Walk floor, authored / intermediate | +1.953 / +1.964 mm |
| Contact anchor / sampled skin step error | 0.000700 / 0.188618 mm maximum |
| Godot pose bounds error | 0.048637 mm maximum |
| Godot cross-fade / viewer floor minima | -2.115 / -1.159 mm; within existing -3 mm limit |
| Visual inspection | Blender front pose strip and matched Godot upper-body pose sheet inspected |
| Naturalness / feel | Pending human normal-speed review |

Godot headless editor import, `test_locomotion.gd`, `test_locomotion_viewer.gd`,
GPU `--capture`, `--record`, `--record --side-view`, `--record --travel`, and
`encode_walk_preview.py --baseline <saved-preview-folder> --comparison-name shoulders`
all exited 0. Python syntax, local documentation links, source/export hashes and
`git diff --check` checked. The installed command paths and reproduction workflow
remain those recorded in the [preceding review](WALK_PUSHOFF_REVIEW.md).

The comparison report is [shoulders_metrics.json](../tools/blender/locomotion_previews/shoulders_metrics.json).
Its shoulder line joins the upper-arm bone heads; height difference excludes common
vertical body motion. A temporary Blender comparison script at
`%TEMP%/gauntlands-compare-shoulders.py` produced the source measurements.

Limits: no physical controller, uneven terrain, new-model recreation or artistic
sign-off. Region-based sampled collision checks are not exhaustive. Exporter
warnings concerning reduction above eight weights and first texture sampler
remain; the delivered export was tested. Existing CC0 MPFB provenance continues.

## Review artifacts

- [Three-quarter before/after](../tools/blender/locomotion_previews/shoulders_before_after.gif)
- [Side before/after](../tools/blender/locomotion_previews/shoulders_side_before_after.gif)
- [Upper-body poses](../tools/blender/locomotion_previews/shoulders_contact_sheet.png)
- [Forward travel](../tools/blender/locomotion_previews/walk_travel.gif)
- [Blender report](../tools/blender/locomotion_previews/validation.json)
- [Godot report](../tools/blender/locomotion_previews/godot_validation.json)
- [Viewer report](../tools/blender/locomotion_previews/viewer_validation.json)

R2/R6 receiving result: technical checks pass. Built derivative is loaded in
connected Blender with Walk selected, frames 1-73. Human review should judge
whether the shoulders feel connected to the step without looking exaggerated.
