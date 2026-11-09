# Foot-angle polish and three-view review - 9 November 2026

Historical pass: followed by the [relaxed unarmed upper-body pass](WALK_UPPER_BODY_REVIEW.md).
Shared reports/media now describe the successor; numbers below remain historical.

## Scope and review contract

User authorised another polish pass and explicitly made isometric, three-quarter
and top-down the model's target sign-off views. The durable requirement and
repeatable camera presets are recorded in [Human Model Review](HUMAN_MODEL_REVIEW.md).
R3 leads; R4 camera/readability review and R2/R6 integration/validation were
performed sequentially by the same agent. Existing `human-prototype-01`,
Jonty303/Gauntlands. No commits, pushes, branches or merges; artistic sign-off pending.

## Changes and handoff

The three requested cameras were added to the [viewer](../prototype/locomotion.gd),
along with an eight-facing selector. Isometric is the default; legacy low-angle
views remain for diagnosis. Controls sit left of the model. Review captures hide
UI, retain matched lighting/scale, and use a safe explicit up vector for top-down.
The [encoder](../tools/blender/encode_review_views.py) produces normal-speed loops,
before/after comparisons and four-pose/eight-facing sheets for every view.
[Viewer tests](../prototype/tests/test_locomotion_viewer.gd) exercise actual camera
button signals, elevations, projection, finite top-down orientation and facings.

Baseline raised/top-down inspection exposed the rigidly parallel foot headings.
The bounded animation polish in the [generator](../tools/blender/build_locomotion.py)
adds 4 degrees of outward heading to each foot during Walk. Rocker offsets rotate
around a common ankle reference, keeping the heading constant through heel, ball
and toe contact. This avoids a planted-foot swivel or a jump when the pivot stage
changes. [Export validation](../tools/blender/test_locomotion.py) checks actual
heading against the requested value with a new 0.1-degree tolerance.

Pelvis/head ranges, gait timing and all prior curve parameters are unchanged.
The underlying knee and shoulder passes remain. Ankle targets change slightly
with rocker orientation; planted-contact stability was tested, not assumed.
Idle sampled bounds match exactly. Original source preserved; nine source shape
keys, 137 bones, packed textures, 8-influence GLB, metres and established axes;
60 Hz bake, 4-second Idle, 1.2-second Walk, 0.9 m/s, 60% stance and half-cycle
leg offset remain. No gameplay/controller or geometry changes. Sprite dimensions
and facing order do not apply to these 3D review artifacts.

R3 -> R2/R6 artifacts: generator, validator, viewer/tests, encoder, README and raw-frame
ignore entry; [editable derivative](../assets/Blender%20Models/Human-Male-Locomotion.blend),
[GLB](../prototype/assets/human_locomotion.glb), refreshed pose bounds, reports and
media. The [metrics](../tools/blender/locomotion_previews/foot_angle_metrics.json)
record before/after preservation. Backup:
`%TEMP%/gauntlands-views-before-20261109-092329`.

## Evidence and findings

Blender 5.2.3 LTS build/full export validation exited 0: 241 Idle frames,
73 Walk frames and 72 half-frame floor/knee-speed samples. Godot 4.5.2 editor
import, `test_locomotion.gd` and `test_locomotion_viewer.gd` exited 0. Existing
limits were not relaxed.

| Check | Result |
| --- | --- |
| Foot heading maximum error across the cycle | 0.000066 degrees; pass |
| Contact anchor / sampled skin step error | 0.000726 / 0.187784 mm; pass |
| Walk floor, authored / intermediate | +1.953 / +1.965 mm |
| Knee speed / cyclic acceleration | 5.177 degrees/frame / 1.787 degrees/frame squared; pass |
| Hand-thigh clearance / intersections | 15.813 mm / zero |
| Sampled hand-self, body-cloth, cloth-self, inside-vertex checks | Zero |
| Loop endpoint vertex difference | Zero |
| Godot pose bounds error | 0.050187 mm; pass |
| Godot cross-fade / viewer floor minima | +0.533 / +1.668 mm; pass |
| Camera buttons / eight facing selections | Pass, including vertical camera orientation |

GPU baseline and current `--record --review` each captured 108 loop frames and
96 facing/pose images. Legacy capture, side/travel recordings, both encoders and
a UI-layout capture exited 0. The three cycle pose strips, all eight-facing
sheets and viewer UI were inspected. Source/export hashes, Python syntax,
UTF-8 source encoding, documentation links, GIF cadence and diff whitespace were
checked. An initial script-encoding issue was corrected before successful imports.

Visual findings from the captured poses:

- Isometric gives the clearest combination of full-body silhouette and foot roll.
- Raised three-quarter retains readable landing/recovery poses; foreshortening
  reduces some far-leg separation, especially when facing the camera directly.
- Top-down exposes foot headings and arm/shoulder silhouette. Around the passing
  pose the torso obscures much of the legs, so knee bend and vertical foot
  clearance are not assessable from that view alone. This remains a sign-off
  consideration, not a claim that the visibility limitation was removed.

R2/R6 technical gates pass. Human normal-speed feel and model acceptance remain
pending. Captured poses and sampled checks are not exhaustive continuous-motion,
collision or skin-twist proofs. No fresh-character recreation, physical controller,
uneven terrain or live eight-direction movement test. Existing exporter
weight/sampler warnings and CC0 MPFB provenance continue.

## Review artifacts

- [Three-view loop](../tools/blender/locomotion_previews/review_views.gif)
- [Isometric comparison](../tools/blender/locomotion_previews/review_isometric_before_after.gif)
- [Raised 3/4 comparison](../tools/blender/locomotion_previews/review_three_quarter_before_after.gif)
- [Top-down comparison](../tools/blender/locomotion_previews/review_top_down_before_after.gif)
- [Isometric facings](../tools/blender/locomotion_previews/review_isometric_facings.png)
- [Raised 3/4 facings](../tools/blender/locomotion_previews/review_three_quarter_facings.png)
- [Top-down facings](../tools/blender/locomotion_previews/review_top_down_facings.png)
- [Viewer UI](../tools/blender/locomotion_previews/review_viewer_ui.png)
- [Blender report](../tools/blender/locomotion_previews/validation.json)
- [Godot report](../tools/blender/locomotion_previews/godot_validation.json)
- [Viewer report](../tools/blender/locomotion_previews/viewer_validation.json)

Loops contain 36 images over 1.2 seconds. Both raw and encoded camera settings
are recorded in the [manifest](../tools/blender/locomotion_previews/review_cameras.json).
The revised derivative is open in connected Blender with Walk selected.
