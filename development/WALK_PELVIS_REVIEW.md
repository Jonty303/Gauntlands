# Walk pelvis revision - 8 November 2026

Historical pelvis pass. Current generated assets and validation reports now
reflect [the shoulder/arm revision](WALK_ARMS_REVIEW.md). Its original
before/after preview and pelvis contact sheet remain unchanged.

## Scope, ownership and handoff

Authorised follow-on to the heel/toe pass, addressing hip movement and weight
transfer on existing `human-prototype-01` in Jonty303/Gauntlands.
R3 primary; R2 integration and R6 QA performed sequentially by the same agent.
No independent review or human artistic sign-off claimed. No commits, pushes,
branches or merges created. Existing unrelated uncommitted work preserved.

R3 -> R2/R6: updated [generator](../tools/blender/build_locomotion.py),
[export validation](../tools/blender/test_locomotion.py),
[editable derivative](../assets/Blender%20Models/Human-Male-Locomotion.blend),
[GLB](../prototype/assets/human_locomotion.glb), regenerated bounds references,
build/validation reports and GPU previews. Accepted 180 cm model hash unchanged.
Pre-edit scripts, source/export and evidence backed up to
`%TEMP%/gauntlands-pelvis-before-20261108-214221`.

## Motion and interfaces

- Pelvis lateral root amplitude: 24 mm towards the supporting leg.
- Pelvic yaw: +/-3 degrees, bringing the advancing side forward.
- Pelvic tilt: +/-1.5 degrees, allowing the unsupported side to dip.
- Vertical amplitude: 12 mm about a -45 mm rest offset, with the low point
  delayed 0.048 seconds after contact. Analytic reach protection retained.
- Counter-rotation distributed across five spine bones. Chest yaw opposes
  pelvis yaw at half amplitude; chest tilt retains half pelvis tilt.
- Head orientation retains only 0.3 degrees yaw and 0.225 degrees tilt at peak;
  it follows body translation rather than being position-locked.
- Existing arm swing and analytic leg solve retained. Knee/shoulder positions
  naturally respond to the revised body motion.

Preserved: 137-bone hierarchy, nine source shape keys, underwear, provenance,
metres, Blender Z-up/-Y-forward, Godot Y-up/+Z-facing, 60 Hz bake, 4-second Idle,
1.2-second Walk, 0.9 m/s reference travel, half-cycle leg offset, 60% stance,
heel/toe articulation, viewer blend/stop rules and eight-influence GLB export.
Every authored ankle target was compared with the previous build and is exactly
unchanged. No gameplay/controller, body modelling, clothing or new rig work.

Task-local motion guard: knee flex changes by less than 6 degrees per authored
60 Hz sample, with more than 5 degrees remaining flex. This is a regression
check against abrupt changes/locking, not a biomechanical realism certificate.
Existing contact/geometry limits are retained. No performance claims made.

## Commands and observed results

Using Blender 5.2.3 LTS and Godot 4.5.2 stable, ran:

1. `build_locomotion.py` on `Human-Male-180cm.blend` with background factory startup.
2. `test_locomotion.py -- --quick`, then the complete `test_locomotion.py`.
3. Godot `--headless --editor --path prototype --quit`.
4. Godot `--headless --path prototype --script res://tests/test_locomotion.gd`.
5. Godot `--headless --path prototype --script res://tests/test_locomotion_viewer.gd`.
6. Actual GPU `--path prototype -- --capture` and `--record`, then
   `encode_walk_preview.py` using the existing temporary Pillow installation.
7. Python syntax compilation, reference/source comparisons, handoff link checks
   and `git diff --check`.

All completed successfully. Full Blender report has `quick: false` and covers
241 Idle plus 73 Walk frames. Original diagnostic regression was not rerun:
no diagnostic asset, shared engine code or import settings changed in this pass.

| Gate | Observed result |
| --- | --- |
| Original source / derivative reopen | Pass: source hash preserved, nine shape keys, packed textures |
| Body/cloth geometry | Zero tested body-cloth intersections, cloth self intersections or inside-cloth vertices |
| Loop seam | Zero endpoint vertex difference |
| Walk floor minimum | 1.850 mm above plane |
| Contact anchor step error | 0.000730 mm maximum |
| Sampled sole vertex step error | 0.188440 mm maximum |
| Sampled contact vertex height | 8.472 mm maximum |
| Pelvis lateral range | 48.487 mm (previous live source: 28 mm) |
| Pelvis vertical range | 23.996 mm (previous live source: 54 mm) |
| Head lateral range | 26.918 mm (previous live source: 28 mm) |
| Head vertical range | 23.916 mm (previous live source: 54.678 mm) |
| Knee flex range | 20.717 to 64.097 degrees |
| Maximum knee change per 60 Hz sample | 5.010 degrees, within 6-degree task guard |
| Godot pose agreement | 0.048518 mm maximum bounds error |
| Cross-fade floor minimum | -1.764 mm, within existing -3 mm tolerance |
| Actual viewer transitions | Pass; minimum -1.170 mm |
| Visual inspection | Blender front pose strip plus Godot side/back and before/after cycle frames reviewed |
| Human acceptance / gamepad | Pending / not tested |

[Measured motion and prior baseline](../tools/blender/locomotion_previews/pelvis_revision_metrics.json)
records source-baseline versus exported-revision measurements explicitly.
Small export rounding differences are expected. Idle sampled bounds were also
compared against the previous exported report; the measured delta is in that file.

Checks cover authored 60 Hz samples, not every possible interpolation or terrain.
Representative sole vertices are not a full contact patch. Counter-motion is
an authored approximation, not simulation or motion capture. Existing export
warnings (more than eight weights reduced; first texture sampler used) remain;
the resulting exported geometry is what was validated. Artistic naturalness
still requires the owner's judgement of the loop.

## Review

- [Before/after loop](../tools/blender/locomotion_previews/pelvis_before_after.gif)
- [Updated walk](../tools/blender/locomotion_previews/walk.gif)
- [Before/after poses](../tools/blender/locomotion_previews/pelvis_contact_sheet.png)
- [Full Blender checks](../tools/blender/locomotion_previews/validation.json)
- [Godot pose/blend checks](../tools/blender/locomotion_previews/godot_validation.json)
- [Viewer checks](../tools/blender/locomotion_previews/viewer_validation.json)

R2/R6 receiving review: technical integration accepted for human visual review.
The regenerated derivative is loaded in connected Blender with Walk selected
and range 1-73. Next owner: human gait review; no first-character milestone
sign-off or further feature scope inferred.
