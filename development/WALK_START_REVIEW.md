# Setting off with forward intent — 9 November 2026

Historical momentum pass. The reported chest-entry surge is addressed in
[the chest-entry correction](WALK_START_CHEST_REVIEW.md). Shared source/export
files and the full sequence preview now reflect that correction.

## Scope and handoff

User requested the proposed setting-off change immediately. R3 Character &
Technical Artist leads; R2/R4/R6 integration, sampled visual review and QA are
performed sequentially by the same agent. Existing `human-prototype-01`, no new
branch, commit, tag, push or merge. Human feel approval remains pending.

Only WalkStart is retuned. Idle, the approved Walk and both stopping clips are
preserved and compared with the saved first v0.2 export. The approved v0.1 tag
remains `f4579d0`. No equipment, controller, terrain or extra animation state.

Baseline source/export/scripts and complete captures were saved at
`%TEMP%/gauntlands-start-before-20261109-105730`. The first-pass build/validation
reports and sequence GIF are also retained under `locomotion_v02/first_pass_*`.

## Change

WalkStart is 0.7 seconds (43 samples at 60 Hz), previously 0.8 seconds. Planted
preparation before the left foot lifts is 0.1 seconds, previously 0.2 seconds.
The swing still has 0.6 seconds; this does not simply speed up the entire clip.

The body inclines forward by an authored maximum of 2.5 degrees about the ground
origin, rather than folding at the waist. An additional 12 mm pelvis translation
leads the step. The inclination and translation fade out before the unchanged
Walk contact pose. The resulting hip displacement is larger than 12 mm because
the whole-body inclination also moves the pelvis forward.

Virtual acceleration starts at 0.14 seconds rather than 0.32. A smooth asymmetric
speed ramp retains the same 0.216 m total travel and 0.9 m/s exit speed. Both
planted-foot targets compensate this travel. The final foot placement, toe-out,
loose fists and Walk entry phase remain unchanged. The lean settles later to
prevent a small backward hip hesitation detected during this pass.

The viewer and encoder derive capture timings from the actual clip duration.
The comparison uses equal clock time from the same Idle request point, with
matched cameras, scale and lighting. It therefore shows the earlier start and
Walk entry rather than retiming both versions to disguise the difference.

## Artifacts and reproduction

R3 -> R2/R6: [generator](../tools/blender/build_transitions.py),
[editable source](../assets/Blender%20Models/Human-Male-Locomotion-v0.2.blend),
[GLB](../prototype/assets/human_locomotion_v02.glb),
[viewer](../prototype/locomotion_v02.gd),
[export tests](../tools/blender/test_transitions.py),
[Godot tests](../prototype/tests/test_transitions.gd), reports and review media.
Interfaces remain metres, established Blender/Godot axes, 137 bones, nine source
shape keys, packed textures, eight exported skin influences and 60 Hz baking.

Run the existing v0.2 build/test/import commands. For the additional preservation
comparison pass `-- --baseline <saved-human_locomotion_v02.glb>` to Blender's
`test_transitions.py`. Capture with `godot --path prototype -- --record`, then:

```powershell
python tools/blender/encode_transition_preview.py --baseline <saved-previews/frames>
```

[Before/after, three views](../tools/blender/locomotion_v02/start_before_after.gif) ·
[Full revised sequence](../tools/blender/locomotion_v02/momentum_sequence_review.gif) ·
[Comparison pose sheet](../tools/blender/locomotion_v02/start_before_after_poses.png) ·
[Source hip measurements](../tools/blender/locomotion_v02/momentum_start_metrics.json).

## Evidence

Blender 5.2.3 LTS generator and full export validator exited 0. Godot 4.5.2
headless editor import and `test_transitions.gd` exited 0. The export suite
covered 382 authored new-clip poses plus 378 intermediate poses. Runtime checks
included starts from four Idle phases, stops from six Walk phases, pause,
changed requests during transitions and large elapsed-time steps.

| Check | Result |
| --- | --- |
| Approved Walk exported animation channels | Exact match |
| Idle and both stop animation channels vs saved v0.2 | Maximum component error 3.72422178e-07; within 1e-6 float tolerance |
| Start authored/intermediate floor minimum | +2.413752 mm |
| Start body/cloth, cloth-self and hand/core intersections | Zero |
| Start hand/core minimum clearance | 45.672134 mm |
| Start knee maximum step / acceleration | 4.647452 degrees / 2.092224 degrees per frame squared |
| Start-to-Walk knee acceleration | 2.092224 degrees per frame squared |
| Start planted anchor / sampled skin maximum step drift | 0.000484 / 0.000460 mm |
| Backward hip excursion including virtual travel | 0.067003 mm |
| Largest new-clip endpoint surface difference | 0.005071 mm |
| Godot/Blender bounds maximum difference | 0.050187 mm |
| Runtime transition floor minimum | +2.076523 mm |

Existing floor, contact, clearance and knee limits were retained. A new task-local
maximum 0.1 mm backward hip-excursion gate checks the requested forward continuity,
including half-frame poses. The initial 3.173 mm hesitation was reduced by delaying
the lean and hip-translation settles; the limit was not relaxed. These remain
sampled checks, not a guarantee of continuous collision-free motion.

At 0.1 seconds, the source pelvis has moved 38.272 mm forward relative to its
initial in-place position, compared with essentially zero before. This measurement
excludes virtual travel; it isolates the added body preparation. Parameters and
per-frame travel are recorded in [build.json](../tools/blender/locomotion_v02/momentum_build.json).

GPU capture exited 0: 756 sequence frames and 96 facing/clip poses. The revised
sequence is 8.4 seconds; the matched before/after is 2.4 seconds, both 30 fps.
The comparison starts with 0.8 seconds of Idle before the identical Walk request.

R2/R6 technical handoff: pass. Normal-speed feel approval remains with the owner.
Equipment compatibility, controller responsiveness, terrain and other body
proportions remain unverified. Existing exporter weight/sampler warnings remain.
The v0.1 files and tag are preserved; this v0.2 work remains uncommitted.

Final visual review: the matched three-view pose sheet and all three eight-facing
sheets were inspected. The earlier forward body preparation and earlier leg
recovery are visible at equal elapsed times; top-down primarily reveals the
forward torso shift and arm silhouette. No new obvious silhouette or clothing
defect was found in these sampled poses. Normal-speed feel remains for human
review. GIF durations, capture counts, matching cameras, current report hashes,
Python syntax, document links and diff whitespace were checked.
