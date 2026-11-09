# Running prototype — v0.3 approved checkpoint

Authorised on 9 November 2026 after acceptance of the chest-entry correction.
Local v0.2 checkpoint: `12b2b0b`, tag `human_male_prototype_v0.2`.
R3 leads animation; R2/R4/R6 checks are performed by the same agent.

Scope: relaxed unarmed Run and left/right contact-matched WalkToRun/RunToWalk,
with a three-view review sequence. Retain v0.1 and v0.2 assets and animation.
No equipment, terrain, controller gameplay, new branch, merge or push.

Trial parameters: Run 0.8 s, reference travel 2.2 m/s, 40% stance per leg,
0.08 s flight between steps, 6-degree torso lean. Gait changes last 1.0 s,
retain endpoint phase speeds and enter/leave at matching left or right contact.
Existing units, axes, rig, textures, loose fists and 60 Hz export remain.

Task-local run gates set before evaluation: floor >= -3 mm, hand/core clearance
>= 5 mm, no body/cloth penetration, knee step < 12 degrees per 60 Hz frame,
knee acceleration < 4 degrees/frame squared, planted anchor drift < 0.1 mm
per frame within a contact stage. Boundary mesh mismatch < 0.1 mm. These are
prototype limits for the faster movement, not changes to the approved walk gates.
Runtime checks cover both lead variants, pause, repeated requests, large time
steps and 30/60/120 Hz. Review isometric, raised 3/4, top-down and eight facings.
Owner approved this run pass on 9 November 2026 and requested its commit.

The run exposes centre-front underwear deformation in the exported skin.
The v0.3 derivative adds up to 8 mm of local front-seam ease. Body geometry,
rig and frozen v0.2 files are unchanged. A subdivision trial did not resolve
cloth folding and was removed; the original garment topology is retained.
Retained clip garment clearance is checked again because this fit correction
affects their v0.3 rendering. Knee recovery peaks earlier, behind the body,
then unfolds into landing rather than carrying a high knee far forward.

## Artifacts and reproduction

- [Authoring script](../tools/blender/build_run.py)
- [Editable v0.3 source](../assets/Blender%20Models/Human-Male-Locomotion-v0.3.blend)
- [v0.3 GLB](../prototype/assets/human_locomotion_v03.glb)
- [Godot review scene](../prototype/locomotion_v03.tscn) and [state logic](../prototype/locomotion_v03.gd)
- [Export tests](../tools/blender/test_run.py) and [runtime tests](../prototype/tests/test_run.gd)

```powershell
blender --background --factory-startup --python-exit-code 1 --python tools/blender/build_run.py
blender --background --factory-startup --python-exit-code 1 --python tools/blender/test_run.py
godot --headless --editor --path prototype --quit
godot --headless --path prototype --script res://tests/test_run.gd
godot --path prototype res://locomotion_v03.tscn -- --record
python tools/blender/encode_run_preview.py
```

Substitute installed executable paths; the encoder uses the existing Pillow
preview dependency. The generator loads the frozen v0.2 source. Run has 49
endpoint-inclusive samples; each one-second bridge has 61. Left lead is phase
zero and right lead phase one-half. Virtual bridge travel is 1.55 m, with smooth
speed changes between 0.9 and 2.2 m/s. The in-place root and moving ground reference
remain an animation-review interface, not implemented character movement.

Requests wait for the next half-cycle contact, complete an authored bridge and
retain the latest intent. A request from Idle uses the approved WalkStart first;
an Idle request during Run uses RunToWalk followed by WalkStop. Direct run starts,
run stops, turning and equipment poses remain outside this slice.

The preview sequence exercises the full Idle -> Walk -> Run -> Walk -> Idle
chain. Separate right-lead clips and eight-facing Run pose sheets accompany it.
[Run loop](../tools/blender/locomotion_v03/run_review.gif) ·
[Full sequence](../tools/blender/locomotion_v03/sequence_review.gif) ·
[Right-lead acceleration](../tools/blender/locomotion_v03/WalkToRunR.gif) ·
[Right-lead deceleration](../tools/blender/locomotion_v03/RunToWalkR.gif).


## Technical evidence

Blender 5.2.3 LTS authoring/export and final `test_run.py` exited 0. Godot
4.5.2 headless editor import and `test_run.gd` exited 0. Validation report and
build manifest match GLB SHA-256 `98e80de0c02fd70007d7949a861b012bf1b9b349df59b914c72585a3a79171c7`.

| Check | Observed result |
| --- | --- |
| v0.1 / v0.2 frozen source, exports and generators | All manifest hashes preserved |
| All five v0.2 animation channels in v0.3 | Exact match |
| New authored / intermediate poses | 293 / 288 |
| Older-clip fabric clearance regression | 155 sampled poses; zero body intersections or inside vertices |
| Body/cloth, cloth-self and hand/core intersections in new clips | Zero |
| Minimum floor clearance in new clips | +1.785131 mm |
| Maximum knee step / acceleration | 6.176076 degrees / 3.802202 degrees per frame squared |
| Minimum hand/core clearance | 16.814698 mm |
| Maximum contact-anchor / sampled skin step drift | 0.002816 / 0.435617 mm |
| Maximum endpoint surface mismatch | 0.001208 mm |
| Godot/Blender maximum bounds difference | 0.050306 mm |
| Gait changes from five phases, both directions, 30/60/120 Hz | All 30 cases pass; travel agrees within 0.01 mm |
| Pause, changed requests, restart intent and large time steps | Pass |

Contact anchors are rig-space points. Sampled sole heights reach about 10 mm
through toe roll; these diagnostics do not certify exact continuous skin-ground
contact. The loop includes verified both-feet-clear samples, while the intended
stance timing remains 40% per leg. Limits are unchanged from the brief above.
Existing exporter influence-reduction and texture-sampler warnings remain.

R3 -> R2/R6 handoff: source, GLB, phase/travel manifest, review scene and test
reports accepted technically for this prototype slice by the same agent.
The owner accepted the run's feel on 9 November 2026. Future equipment compatibility
remains unverified. Full gameplay, direct run starts/stops, terrain,
retargeting and performance budgets are not certified by this animation pass.

The v0.2 checkpoint is committed/tagged locally. This v0.3 pass is approved for
checkpointing as `human_male_prototype_v0.3` on `human-prototype-01`; no push or merge was requested. Unrelated RPG notes and
diagnostic import changes were left out of the checkpoint and preserved.


## Sampled visual review

R4 review by the same agent: all three eight-facing Run sheets and the matched
three-view acceleration/deceleration pose sheet inspected. The run has a clear
arm/leg silhouette and alternating recovery; the raised views show the landing
and unfolding leg. Top-down chiefly shows arm swing and shoulder opposition,
with natural leg occlusion. No new obvious clothing or silhouette defect was
found in these sampled poses. Eight side-on source poses were also inspected.
This is not a claim of owner normal-speed sign-off.

GPU capture exited 0 and produced 1,077 frames: 729 full-sequence frames,
252 standalone Run/right-lead transition frames and 96 facing poses. Encoded
Run is 24 frames / 0.8 s; sequence 243 frames / 8.1 s; right-lead bridges each
30 frames / 1 s. Captured clip names match the intended sequence frame-for-frame;
camera settings match v0.2 exactly. GIF timing, Python syntax, relative links,
report hashes and diff/untracked-text whitespace were checked.

[Transition poses](../tools/blender/locomotion_v03/transition_poses.png) ·
[Isometric facings](../tools/blender/locomotion_v03/isometric_facings.png) ·
[Raised 3/4 facings](../tools/blender/locomotion_v03/three_quarter_facings.png) ·
[Top-down facings](../tools/blender/locomotion_v03/top_down_facings.png).
