# Walk shoulder and arm revision - 8 November 2026

Historical arm pass. Current source, exports and validation reports are updated
by [the loose-fist and gait refinement](WALK_FISTS_GAIT_REVIEW.md). The earlier
arm comparison GIF and contact sheet remain unchanged.

## Scope and handoff

User authorised this next pass after the pelvis revision: shoulder motion,
arm timing, softer elbows and restrained hand follow-through. Existing
`human-prototype-01` in Jonty303/Gauntlands only. R3 primary; R2 integration and
R6 QA performed sequentially by one agent, with no independent sign-off.
Human artistic acceptance remains pending. No commits, pushes, branches or merges.

R3 -> R2/R6: updated [generator](../tools/blender/build_locomotion.py),
[export checks](../tools/blender/test_locomotion.py),
[Blender derivative](../assets/Blender%20Models/Human-Male-Locomotion.blend),
[GLB](../prototype/assets/human_locomotion.glb), bounds reference, generated
build/validation reports, screenshots and animation previews. Existing source,
export, scripts and previews backed up before editing to
`%TEMP%/gauntlands-arms-before-20261108-221721`.

## Motion contract

- Existing chest rotation drives arm directions. Clavicles add a restrained
  +/-1 degree yaw, following the arm swing without added shrugging.
- Upper-arm phase lags by 0.025 cycle (30 ms); forearm phase by 0.045 (54 ms).
  Opposite-arm/opposite-leg rhythm is retained.
- Reduced outward arm direction brings the hands slightly closer to the body.
- Forearm sagittal flex varies from 12 to 24 degrees, more flex on forward swing.
  Measured 3D elbow angles also include the lateral angle between arm segments.
- Wrist follow-through is +/-2 degrees, phased at 0.065 cycle (78 ms).
- Fingers 2-5 have mild static joint curls of 5/8/5 degrees towards the palm;
  thumb rest pose remains unchanged. No grasping/fist system introduced.

Preserved interface: 137 bones, nine editable source shape keys, underwear,
materials/provenance, metres, Blender Z-up/-Y-forward, Godot Y-up/+Z-facing,
60 Hz bake, 4-second Idle, 1.2-second Walk, 0.9 m/s reference travel, heel/toe
roll, pelvis/spine/head motion and viewer transition rules. Eight-influence
export remains. No model, gameplay/controller, costume or rig-framework changes.

Original accepted-model hash and every authored ankle target match the previous
build. Every exported pelvis/head/knee sample and foot-contact sample matches
the pelvis-pass report exactly. Idle sampled mesh bounds also match exactly.

## Validation and evidence

Blender 5.2.3 LTS; Godot 4.5.2 stable. Ran these steps, all exit 0:

1. `build_locomotion.py` from accepted `Human-Male-180cm.blend`, background factory startup.
2. `test_locomotion.py -- --quick`, then full `test_locomotion.py`.
3. Godot `--headless --editor --path prototype --quit`.
4. Godot `--headless --path prototype --script res://tests/test_locomotion.gd`.
5. Godot `--headless --path prototype --script res://tests/test_locomotion_viewer.gd`.
6. GPU `--path prototype -- --capture` and `--record`, then `encode_walk_preview.py`
   using the existing temporary Pillow installation.
7. Python syntax compilation, preservation comparisons, documentation links and
   `git diff --check`.

Final export validation is full (`quick: false`): 241 Idle and 73 Walk frames.
Original diagnostic regression was not rerun; its assets and shared engine code
were not changed. No physical controller testing or performance claim.

| Gate | Result |
| --- | --- |
| Source preserved / derivative reopened | Pass; original hash, nine shape keys, packed textures |
| Body/cloth checks | Zero body-cloth intersections, cloth self intersections or inside-cloth vertices |
| Loop seam | Zero endpoint vertex difference |
| Walk floor minimum | 1.850 mm above plane |
| Contact anchor / sampled skin step error | 0.000730 mm / 0.188440 mm maximum |
| Tested hand-region/thigh intersections | Zero |
| Tested hand-region/thigh clearance | Minimum 24.303 mm |
| Measured elbow flex | 15.824 to 26.442 degrees |
| Maximum elbow change per authored frame | 0.492 degrees |
| Lower-body/head regression | Exact match to preceding exported samples |
| Godot pose bounds agreement | Maximum error 0.048518 mm |
| Cross-fade minimum floor | -1.764 mm; within existing -3 mm tolerance |
| Actual viewer transitions | Pass; minimum -1.170 mm |
| Visual inspection | Blender cycle strip and front/back/side views, Godot side pose and before/after cycle poses reviewed |
| Human artistic acceptance | Pending |

New task-local safety checks require more than 5 mm hand-region/thigh clearance,
zero region intersections and less than 6 degrees elbow change per 60 Hz sample.
The regions are selected spatially in the exported bind mesh, independently of
animation curves: hand vertices beyond +/-0.48 m X and below 1.25 m Z; thigh/lower
trunk vertices within +/-0.30 m X and below 1.10 m Z. These are model-specific
regions, not an exhaustive hand/finger/body self-collision certificate. No
inter-finger collision test was added; the small curl was visually reviewed.

Checks cover authored 60 Hz frames, not all subframes or terrain. Naturalness
still needs human judgement. Existing export warnings about reducing weights
over eight and choosing the first texture-node sampler remain; actual exported
geometry was tested. Source materials retain the earlier CC0 MPFB provenance;
animation is project-authored, without downloaded motion capture.

## Review artifacts

- [Before/after loop](../tools/blender/locomotion_previews/arms_before_after.gif)
- [Updated walk](../tools/blender/locomotion_previews/walk.gif)
- [Before/after poses](../tools/blender/locomotion_previews/arms_contact_sheet.png)
- [Arm metrics and preservation checks](../tools/blender/locomotion_previews/arms_revision_metrics.json)
- [Full Blender report](../tools/blender/locomotion_previews/validation.json)
- [Godot pose/blend report](../tools/blender/locomotion_previews/godot_validation.json)
- [Viewer report](../tools/blender/locomotion_previews/viewer_validation.json)

R2/R6 receiving result: technically accepted for human visual review. The new
source is loaded in connected Blender with Walk selected and range 1-73.
Next owner: human gait review. No first-character milestone sign-off inferred.
