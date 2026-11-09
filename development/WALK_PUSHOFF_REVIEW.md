# Push-off and toe-release pass - 8 November 2026

Historical pass: followed by the [shoulder follow-through pass](WALK_SHOULDERS_REVIEW.md). Shared reports and current walk previews now describe the later pass.

## Scope and ownership

User requested the next walk iteration after identifying stiff push-off and
emphasising repeatable feel. R3 Character & Technical Artist leads; R2 integration
and R6 checks performed sequentially by the same agent, not independent sign-offs.
Existing `human-prototype-01` in `Jonty303/Gauntlands` only. No commit, push, branch
or merge. Human acceptance of the walk and first character remains pending.

Observable target: forefoot support progresses to a brief toe-tip roll, the foot
continues rotating through toe-off, and the knee recovers without snapping.
Compare at the same 1.2-second cadence and 0.9 m/s speed, including forward travel.
Technical correctness and artistic feel are separate gates.

Pre-edit derivative, GLB, generator, validator, viewer and previews are backed up
at `%TEMP%/gauntlands-pushoff-before-20261108-231327`.

## Motion and repeatability

[Generator](../tools/blender/build_locomotion.py) now uses explicit pose phases
and Hermite slopes for foot rotation and toe peel. This replaces the zero-speed
arrival and held foot angle around release. The maximum foot pitch stays 38 degrees.

| Cycle phase | Intended action |
| --- | --- |
| 34% | Heel rise begins |
| 50% | Foot pitch 18 degrees, forefoot remains supported |
| 52% | Toe segment begins rolling towards its tip |
| 60% | Release: foot pitch 34 degrees, toe pitch 12 degrees |
| 66% | Foot pitch peaks at 38 degrees during initial recovery |
| 70% | Toe segment has blended back into the airborne foot orientation |
| 82% | Foot pitch 5 degrees, approaching forward placement |
| 100% | Foot pitch -12 degrees for heel contact |

The toe-roll displacement raises the ankle around a point selected from the actual
low front sole. That offset carries into early swing and returns smoothly to zero
by 80% of the cycle. The existing leg solver follows the resulting ankle path;
this coordinates knee recovery without adding a separate conflicting knee control.
Pelvis and upper-body curves retain their previous settings. Loose fists remain.

The initial candidate used a source toe-bone endpoint, and the old contact test
used the imported endpoint. Those differed, because glTF joints do not preserve
Blender bone tail positions. The candidate also exceeded the existing sampled
contact-height limit. Both authoring and validation now select the low front sole
from their respective source/export meshes. For this human the source anchor is
(+/-0.185867, -0.202042, 0.007060) m. Bone contact and actual skinned sole samples
are still checked separately. No tolerance was relaxed.

This selection is an improvement to repeatability, not proof that arbitrary
characters are supported. It still assumes this humanoid layout, flat ground,
Blender axes and a 20 mm lateral selection band. Different proportions and newly
generated characters remain untested.

## Artifacts and interfaces

R3 -> R2/R6: [editable derivative](../assets/Blender%20Models/Human-Male-Locomotion.blend),
[export](../prototype/assets/human_locomotion.glb),
[generator](../tools/blender/build_locomotion.py),
[validator](../tools/blender/test_locomotion.py), regenerated
[bounds](../prototype/tests/locomotion_bounds.json), build/validation reports and previews.

[Viewer](../prototype/locomotion.gd) adds review-only `--record --travel`: two cycles
of actual actor translation past stationary ground marks. Existing interactive
selection and transition behaviour is retained. `.gitignore` excludes raw travel
frames. [Encoder](../tools/blender/encode_walk_preview.py) now reproduces side,
travel and matched before/after GIFs using a saved baseline folder.

Preserved contract: metres; Blender Z-up/-Y-forward, Godot Y-up/+Z-facing;
137 bones, nine source shape keys, packed materials, clothing and source model;
60 Hz bake, 4-second Idle, 1.2-second Walk, 60% stance, opposite leg offset 50%,
0.9 m/s reference travel and 8-influence GLB export. Idle sampled bounds differ
from the preceding pass by at most 0.000015 mm (numerical roundoff). No modelling,
gameplay or controller changes. Sprite dimensions/facing order are not applicable.

## Validation

Blender 5.2.3 LTS, Godot 4.5.2 stable. Final build and full Blender validation exited
0; `passed: true`, `quick: false`. All 241 Idle and 73 Walk authored frames were
checked, plus 72 intermediate Walk floor samples. Source-file hash preserved.

| Gate | Observed result |
| --- | --- |
| Save/reopen, original source, shape keys | Pass; source preserved, nine keys |
| Hand self / body-cloth / cloth self / inside-vertex checks | Zero across authored frames |
| Loop endpoint vertex difference | Zero |
| Walk authored / intermediate floor minima | +1.953 / +1.964 mm |
| Contact anchor / sampled skin step error | 0.000700 / 0.188618 mm maximum |
| Sampled contact height | 10.055 mm, below existing 12 mm limit |
| Knee flex / maximum 60 Hz change | 14.502-66.575 degrees / 5.690 degrees; pass existing limits |
| Hand-thigh clearance / intersections | 14.617 mm minimum / zero |
| Pelvis lateral / vertical range | 55.482 / 23.996 mm, unchanged |
| Godot pose bounds error | 0.048637 mm maximum; pass |
| Godot cross-fade / viewer floor minima | -2.115 / -1.159 mm; pass existing -3 mm limit |
| Rotation continuity | Numeric left/right slopes agree at internal curve keys; nonzero rotation at release |
| Visual inspection | Blender side pose strip, rendered matched foot poses and travelling pose sheet inspected |
| Feel / artistic acceptance | Pending human normal-speed playback review |

Commands actually run (Windows executables referenced by absolute installed paths):

```text
blender --background --factory-startup assets/Blender Models/Human-Male-180cm.blend --python-exit-code 1 --python tools/blender/build_locomotion.py
blender --background --factory-startup --python-exit-code 1 --python tools/blender/test_locomotion.py
godot --headless --editor --path prototype --quit
godot --headless --path prototype --script res://tests/test_locomotion.gd
godot --headless --path prototype --script res://tests/test_locomotion_viewer.gd
godot --path prototype -- --capture
godot --path prototype -- --record
godot --path prototype -- --record --side-view
godot --path prototype -- --record --travel
python tools/blender/encode_walk_preview.py --baseline <saved-preview-folder> --comparison-name pushoff
git diff --check
```

The source asset path with spaces was quoted in execution. All final commands
above exited 0. Python compilation and relative documentation links were also
checked. For exact installed executables: Blender is under
`C:/Program Files/Blender Foundation/Blender 5.2/`; Godot is
`%TEMP%/gauntlands-godot-4.5.2/Godot_v4.5.2-stable_win64_console.exe`.
Pillow is loaded from `%TEMP%/gauntlands-preview-libs` through `PYTHONPATH`.

Known limits: tests sample region-based collisions and flat-ground contact;
intermediate samples check the floor only. No physical controller, terrain or
fresh-character recreation test. Existing exporter warnings about more than eight
weights and first texture sampler remain; the actual delivered export was tested.
Original CC0 MPFB asset provenance continues; animation is project-authored.
The Dikko tutorial supplied discussion context, but this pass does not claim to
implement a fully reviewed tutorial or copy its animation.

## Review

- [Side before/after loop](../tools/blender/locomotion_previews/pushoff_side_before_after.gif)
- [Three-quarter before/after](../tools/blender/locomotion_previews/pushoff_before_after.gif)
- [Forward travel](../tools/blender/locomotion_previews/walk_travel.gif) (position resets after two cycles)
- [Matched foot poses](../tools/blender/locomotion_previews/pushoff_contact_sheet.png)
- [Travelling pose sheet](../tools/blender/locomotion_previews/pushoff_travel_sheet.png)
- [Before/after metrics](../tools/blender/locomotion_previews/pushoff_metrics.json)
- [Blender report](../tools/blender/locomotion_previews/validation.json)
- [Godot report](../tools/blender/locomotion_previews/godot_validation.json)
- [Viewer report](../tools/blender/locomotion_previews/viewer_validation.json)

Receiving result: R2/R6 technical checks pass; human feel judgement remains open.
Source derivative is loaded in connected Blender with Walk selected, frames 1-73.
Next owner is the human reviewer: does the forefoot release flow into recovery,
and does forward travel read as supported steps? Do not treat this as character
sign-off or proof of the from-scratch pipeline.
