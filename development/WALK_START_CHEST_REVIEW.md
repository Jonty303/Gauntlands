# Smooth chest entry from Idle — 9 November 2026

## Request and scope

The owner reported that the whole chest suddenly moved forward when setting off.
R3 Character & Technical Artist leads this correction; R2/R4/R6 reviews are
performed sequentially by the same agent. Preserve the 0.7-second start, approved
Walk, Idle and both stops. No equipment, gameplay/controller or other animation
state is introduced. No new branch, commit, tag, push or merge.

The reported version, scripts and captures are backed up at
`%TEMP%/gauntlands-chest-before-20261109-111358`. Its reports and full preview are
also retained under `tools/blender/locomotion_v02/momentum_*`.

## Diagnosis and correction

The existing entry blend lasts 0.12 seconds, while the authored 2.5-degree
whole-body lean reached its full value in 0.18 seconds and the extra 12 mm hip
translation in 0.12 seconds. A runtime marker on `spine01` showed no instantaneous
pose jump, but forward chest speed peaked at 1.061 m/s at 0.117 seconds, just
before the blend ended. The largest adjacent-frame change in forward displacement
was 8.264 mm. This was a surge through the blend, despite smooth source curves.

The new authored lean is 1.25 degrees. It begins at 0.06 seconds and develops
over 0.30 seconds, following a reduced 6 mm hip lead that develops over 0.20
seconds. Both settle smoothly before the unchanged Walk entry pose. Foot lift,
virtual travel, first-step duration and the runtime blend duration are retained.
This addresses the source motion without changing the animation-state behaviour.

The Godot regression now samples the chest marker during the first 0.30 seconds
of actual playback from four Idle phases. Task-local targets are less than 1 mm
immediate marker jump, less than 0.30 m/s early forward speed, and less than 1 mm
adjacent-frame change in forward displacement at 60 Hz. These are new tuning
checks for this issue, not general biomechanical or project-wide limits. The
reported baseline failed the speed and displacement-change checks before edits.

## Handoff and reproduction

R3 -> R2/R6: [authoring script](../tools/blender/build_transitions.py),
[editable source](../assets/Blender%20Models/Human-Male-Locomotion-v0.2.blend),
[GLB](../prototype/assets/human_locomotion_v02.glb),
[runtime tests](../prototype/tests/test_transitions.gd), comparison encoder and
review evidence. Existing units, axes, rig, materials and import settings remain.

Use the [v0.2 reproduction commands](HUMAN_MALE_PROTOTYPE_V02.md#reproduction).
The export validator accepts `-- --baseline <saved-human_locomotion_v02.glb>`
to compare Idle, Walk and both stops. For this comparison:

```powershell
python tools/blender/encode_transition_preview.py --baseline <saved-previews/frames> --comparison-name chest
```

[Three-view before/after](../tools/blender/locomotion_v02/chest_before_after.gif) ·
[Full corrected sequence](../tools/blender/locomotion_v02/sequence_review.gif) ·
[Comparison poses](../tools/blender/locomotion_v02/chest_before_after_poses.png) ·
[Baseline runtime measurement](../tools/blender/locomotion_v02/chest_entry_before.json).


## Visual review and changed files

The matched before/after pose sheet and all three eight-facing sheets were
inspected. At equal elapsed times, the revised chest remains closer to Idle
through the first tenth of a second, then follows the smaller forward shift.
The side-on Blender samples at frames 1, 7, 13 and 19 show the same progression.
No new obvious silhouette or clothing defect was found in these sampled views.
This is sampled visual evidence; normal-speed feel acceptance remains with the owner.

The authoring changes are in `tools/blender/build_transitions.py`, the generated
v0.2 Blender source, GLB and build manifest. Regression changes are in
`prototype/tests/test_transitions.gd` and `tools/blender/test_transitions.py`.
`tools/blender/encode_transition_preview.py` adds a named comparison output so
this pass preserves the earlier start comparison. README/review links and the
current reports/captures were updated; historical `momentum_*` evidence was kept.
No runtime viewer blend/state logic was changed during this correction.

The initial preservation test flagged stop quaternion component differences of
1.125e-6 against its 1e-6 component cutoff. That component cutoff was replaced
with a comparison of every body/cloth vertex at every authored pose of Idle,
Walk and both stops against the saved export, with a 0.01 mm surface limit.
This measures actual deformation in physical units; component errors remain in
the report as diagnostics. The approved Walk still has its separate unchanged
channel check. Existing contact, clearance, knee and join limits were retained.

GPU capture exited 0: 756 sequence frames and 96 facing poses. The comparison
has 72 frames / 2.4 seconds and the full sequence 252 frames / 8.4 seconds.
All three camera configurations match the saved baseline exactly. Python AST,
relative review links and diff whitespace checks passed. All frozen v0.1 file
hashes match their manifest. Blender is left on WalkStart, frames 1-43, for review.


## Final evidence

Blender 5.2.3 LTS build and final export validator exited 0. Godot 4.5.2
headless editor import and final runtime regression exited 0. Build and validator
hashes match the delivered GLB: `32ef2886fa1319f382fcd03271ab95c67e2b60d30d4a0c1530490cb4ae070d24`.

| Check | Result |
| --- | --- |
| Early chest speed, first 0.30 s, four Idle phases | 1.060858 -> 0.188993 m/s (82.2% reduction) |
| Maximum adjacent-frame change in chest forward displacement at 60 Hz | 8.264476 -> 0.917822 mm |
| Immediate chest position jump | 0.0 m |
| Approved Walk channels and surface poses | Exact match |
| Maximum preserved Idle / stop surface difference | 0.001795 mm |
| Start authored/intermediate floor minimum | +2.414057 mm |
| Start body/cloth, cloth-self and hand/core intersections | Zero |
| Start minimum hand/core clearance | 45.990001 mm |
| Start knee maximum step / acceleration | 4.224609 degrees / 2.092346 degrees per frame squared |
| Start backward hip excursion including virtual travel | 0.000000 mm |
| Godot/Blender bounds maximum difference | 0.050187 mm |
| Runtime transition floor minimum | +2.076523 mm |

Export/deformation checks cover 382 authored new-clip poses and 378 half poses;
the preservation comparison additionally checks all authored poses in Idle,
Walk and both stops. Godot checks include starts from four Idle phases, stops
from six Walk phases, pause/restart, changed transition intent and large time steps.

R3 -> R2/R6 technical handoff: pass for this correction, reviewed by the same
agent. R4 sampled view review: pass; owner feel acceptance remains pending.
Equipment, terrain, alternate start lead and controller gameplay remain outside
this pass. Existing exporter weight/sampler warnings remain. Work is uncommitted
on `human-prototype-01`; the approved v0.1 files and tag are preserved.
