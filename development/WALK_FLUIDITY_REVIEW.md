# Walk fluidity pass - 8 November 2026

Historical pass: superseded by the [push-off and toe-release pass](WALK_PUSHOFF_REVIEW.md). Shared reports and current walk previews now describe the later pass.

## Scope and handoff

User requested another pass on the robotic walk and insufficient heel rise.
R3 Character/Technical Artist lead; R2 integration and R6 validation performed
sequentially by the same agent. Existing `human-prototype-01` in
`Jonty303/Gauntlands`; no commits, pushes, branches or merges. Human artistic
acceptance remains pending.

R3 -> R2/R6 artifacts: [generator](../tools/blender/build_locomotion.py),
[validator](../tools/blender/test_locomotion.py),
[Blender derivative](../assets/Blender%20Models/Human-Male-Locomotion.blend),
[GLB](../prototype/assets/human_locomotion.glb), regenerated bounds, reports and
GPU previews. [Viewer](../prototype/locomotion.gd) adds `--record --side-view`
for review capture; `.gitignore` excludes those raw frames. Snapshot of the
previous generator, validator, derivative, export and previews:
`%TEMP%/gauntlands-fluidity-before-20261108-224816`.

## Motion changes

- Heel rise begins at 34% of the cycle, previously 42%. Maximum authored roll
  increases from 28 to 38 degrees around the existing ball/toe joint. Toes stay
  level during stance; ankle translation compensates for the pivot.
- A quintic swing path matches stance velocity and acceleration at its endpoints.
  Earlier clearance buildup blends a 55 mm early lift component with a 40 mm
  sine-squared component. These are overlapping components, not a 95 mm peak.
  The foot briefly trails after toe-off before preparing for heel contact.
- Lateral hip shift leads by 2.5% of the cycle (30 ms). Its 28 mm authored
  amplitude and the previous bob, yaw, tilt and upper-body motion remain.

Timing was informed by [OUHSC gait terminology](https://www.ouhsc.edu/bserdac/dthompso/web/gait/terms.htm):
heel rise around 35%, roughly 60% stance and early-swing knee flexion. Exact
angles and trajectories here are project-authored tuning, not captured motion
or a physiological standard.

Preserved interfaces: metres; Blender Z-up/-Y-forward and Godot Y-up/+Z-facing;
137 bones, nine source shape keys, clothing/materials, 8-influence GLB export,
60 Hz bake, 4-second Idle, 1.2-second Walk, 0.9 m/s reference speed, 60% stance,
half-cycle leg offset and viewer transitions. Loose fists remain in both clips.
Idle sampled mesh bounds match the previous report exactly. Original source
hash is preserved. Sprite dimensions/facing order and gameplay events are not
applicable to this explicitly requested 3D source-animation pass.

## Validation and limits

Final build completed. Full Blender validation report has `passed: true` and
`quick: false`: 241 Idle and 73 Walk frames, plus 72 intermediate Walk floor
samples. The first candidate exceeded the existing knee-step guard (6.53
versus <6 degrees per 60 Hz frame); its lift curve was revised. No tolerance
was relaxed. Heel marker heights are recorded as diagnostics.

Godot 4.5.2 headless editor import, `test_locomotion.gd`,
`test_locomotion_viewer.gd`, GPU `--capture`, `--record` and
`--record --side-view` all exited 0. Python syntax, local documentation links
and diff whitespace checked. Source Blender is 5.2.3 LTS.

| Gate | Observed result |
| --- | --- |
| Original source, save/reopen, shape keys | Pass; original preserved, nine keys |
| Hand self / body-cloth / cloth self / inside vertices | Zero across authored frames |
| Loop endpoint vertex difference | Zero |
| Walk authored / intermediate floor minima | -0.047 / -0.093 mm; pass existing -3 mm limit |
| Contact anchor / sampled sole step error | 0.000685 / 0.188618 mm maximum |
| Sampled contact height | 8.472 mm; below existing 12 mm limit |
| Stance heel marker maximum | 113.609 mm; diagnostic marker, not mesh measurement |
| Knee flex / maximum 60 Hz change | 14.329-66.518 degrees / 5.747 degrees; pass |
| Pelvis lateral / vertical range | 55.482 / 23.996 mm |
| Hand-thigh clearance / intersections | 14.707 mm minimum / zero |
| Godot pose bounds agreement | Maximum error 0.048637 mm; pass |
| Godot cross-fade / viewer floor minima | -1.976 / -1.102 mm; pass existing -3 mm limit |
| Visual inspection | Blender side pose strip and Godot rendered side contact sheet inspected |
| Artistic acceptance | Unverified; human review pending |

The technical checks do not prove naturalness. Collision tests are region- and
sample-based; intermediate samples test the floor, not all surface collisions.
No terrain or physical-controller test. Existing exporter warnings concerning
weights above eight and first texture sampler remain; tested export is the
actual delivered GLB. Existing CC0 MPFB provenance remains. Shared diagnostic
regression was not rerun because its assets and engine logic were unchanged.

## Review artifacts

- [Before/after at normal cadence](../tools/blender/locomotion_previews/fluidity_before_after.gif)
- [Side-view loop](../tools/blender/locomotion_previews/walk_side.gif)
- [Side poses](../tools/blender/locomotion_previews/fluidity_side_sheet.png)
- [Before/after measurements](../tools/blender/locomotion_previews/fluidity_metrics.json)
- [Blender validation](../tools/blender/locomotion_previews/validation.json)
- [Godot pose/blend validation](../tools/blender/locomotion_previews/godot_validation.json)
- [Viewer validation](../tools/blender/locomotion_previews/viewer_validation.json)

R2/R6 receiving result: technically accepted for visual review, not independent
sign-off. Built derivative loaded in connected Blender with Walk selected,
frames 1-73. Next owner: human review of cadence, push-off and weight transfer.
