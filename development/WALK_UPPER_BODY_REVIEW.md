# Relaxed unarmed upper-body pass - 9 November 2026

## Scope and handoff

User authorised connected chest/shoulder movement and an inward arm arc, with
armour, clothing and weapons to be considered later. Idle, setting off and
stopping were identified as a possible next pass, not implemented here.
R3 Character & Technical Artist leads; R4 visual review and R2/R6 integration
and validation were performed sequentially by the same agent. Existing
`human-prototype-01`, Jonty303/Gauntlands; no commits, pushes, branches or merges.
Human artistic acceptance: approved on 9 November 2026 as the prototype walk; see [v0.1 approval](HUMAN_MALE_PROTOTYPE_V01.md).

Required views follow [Human Model Review](HUMAN_MODEL_REVIEW.md): isometric,
raised three-quarter and top-down, with eight-facing pose sheets. The
[foot-angle pass](WALK_FOOT_ANGLE_REVIEW.md) is the baseline, saved at
`%TEMP%/gauntlands-upper-before-20261109-101001`.

## Change

The [generator](../tools/blender/build_locomotion.py) groups the new settings as
`relaxed_unarmed`. Chest yaw increases from +/-3.2 to +/-4.5 degrees; scapular
yaw from 1.4 to 2.2 degrees, shoulder bank from 0.7 to 0.9 degrees. Arm direction
now incorporates 45% of the difference between chest and shoulder orientation.
Existing shoulder/arm/forearm/wrist phase lags and loose fists are retained.

The forward/back direction coefficient increases from 75 to 90 mm. Forward swing
adds a smooth inward component: 22 mm in the upper-arm direction and 18 mm in
the forearm direction, weighted by the squared forward swing. Return swing adds
4 mm outward in each direction. These are direction-vector controls, not direct
wrist displacements; limb lengths remain fixed. The forward/return weights have
continuous first derivatives at their changeover.

Measured relative to the chest, hand lateral range grows from 3.070 to 51.073 mm.
At the forward extreme the hand is 44.060 mm closer to the torso centre than
before; the return extreme is 4.903 mm farther out. Forward/back wrist range
increases from 340.459 to 399.197 mm. Both sides are mirrored half a cycle apart.

The [validator](../tools/blender/test_locomotion.py) adds a spatially selected
central-body region covering torso and lower body, excluding the arms/hands.
Hand clearance and triangle intersections are checked at all authored Walk
frames and halfway between them. The existing >5 mm hand-clearance threshold
is also applied here; no prior thresholds were relaxed. Region-based tests
remain sampled checks, not exhaustive body self-collision guarantees.

R3 -> R2/R6 artifacts: generator, validator,
[editable derivative](../assets/Blender%20Models/Human-Male-Locomotion.blend),
[GLB](../prototype/assets/human_locomotion.glb), refreshed pose bounds, reports and
review media. Viewer and encoder code are unchanged. Preserved interfaces:
metres, established Blender/Godot axes, 137 bones, nine source shape keys, packed
textures, 8-influence GLB, 60 Hz bake, 4-second Idle, 1.2-second Walk at 0.9 m/s,
60% stance and existing transitions. Sprite dimensions/facing order do not apply.

## Evidence and visual review

Blender 5.2.3 LTS build and full export validation exited 0: 241 Idle frames,
73 Walk frames and 72 half-frame Walk samples. Godot 4.5.2 editor import,
`test_locomotion.gd` and `test_locomotion_viewer.gd` exited 0.

| Check | Result |
| --- | --- |
| Original source / nine source shape keys / save-reopen | Pass |
| Idle sampled bounds | Identical to baseline |
| Authored foot targets / exported stance-contact samples | Identical to baseline |
| Pelvis ranges / knee ranges, speed and acceleration | Identical to baseline |
| Hand/core clearance, authored / intermediate | 12.847 / 13.052 mm minimum |
| Hand/core intersections, authored / intermediate | Zero / zero |
| Hand-thigh clearance / intersections | 12.847 mm / zero |
| Elbow range / maximum 60 Hz change | 15.520-26.669 degrees / 0.517 degrees |
| Sampled hand-self, body-cloth, cloth-self, inside-vertex checks | Zero |
| Loop endpoint vertex difference | Zero |
| Walk floor, authored / intermediate | +1.953 / +1.965 mm |
| Godot pose bounds error | 0.050426 mm maximum |
| Godot cross-fade / viewer floor minima | +0.533 / +1.668 mm |

GPU review capture produced 108 loop images and 96 facing/pose images; legacy
capture/record/side/travel modes and both encoders exited 0. The three cycle
pose strips and all eight-facing sheets were inspected. The inward hand path
is most apparent overhead; raised views show the arm/shoulder silhouette while
retaining the prior leg poses. The existing top-down torso occlusion around
passing poses remains. The project owner subsequently approved this walk on 9 November 2026.
That artistic acceptance is separate from the automated and sampled visual checks above.

[Upper-body metrics](../tools/blender/locomotion_previews/upper_body_metrics.json)
include all-73-frame live-source chest/wrist measurements before and after,
export hashes, clearance and preservation comparisons. Python syntax, diff
whitespace, documentation links, matched camera manifests and GIF timing were
checked. R2/R6 technical gates pass. No physical-controller, uneven-terrain,
fresh-character recreation or equipment compatibility test was performed.
Existing exporter weight/sampler warnings and CC0 MPFB provenance remain.

## Equipment and next pass

This is the relaxed, unarmed baseline. Tuning values are grouped and recorded in
[build.json](../tools/blender/locomotion_previews/build.json); an equipment-profile
loader or layered animation system has not been introduced. Armour will need
its own clearance review, clothing deformation checks, and weapons/shields their
own carrying/gripping poses. Those adaptations can retain the established gait
rhythm while changing upper-body controls.

Idle, setting off and stopping remain the next separate design/animation task.
Current Idle and existing viewer start/stop blending are preserved and tested.

## Review media

- [All three views](../tools/blender/locomotion_previews/upper_review_views.gif)
- [Isometric before/after](../tools/blender/locomotion_previews/upper_isometric_before_after.gif)
- [Raised 3/4 before/after](../tools/blender/locomotion_previews/upper_three_quarter_before_after.gif)
- [Top-down before/after](../tools/blender/locomotion_previews/upper_top_down_before_after.gif)
- [Isometric facings](../tools/blender/locomotion_previews/review_isometric_facings.png)
- [Raised 3/4 facings](../tools/blender/locomotion_previews/review_three_quarter_facings.png)
- [Top-down facings](../tools/blender/locomotion_previews/review_top_down_facings.png)
- [Blender report](../tools/blender/locomotion_previews/validation.json)
- [Godot report](../tools/blender/locomotion_previews/godot_validation.json)
- [Viewer report](../tools/blender/locomotion_previews/viewer_validation.json)

Loops contain 36 images over 1.2 seconds with matched cameras/lighting/scale.
The updated derivative is open in connected Blender, Walk selected.
