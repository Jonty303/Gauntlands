# Blender troubleshooting and lessons

Recorded 9 November 2026. All entries below apply to this human prototype using
Blender 5.2.3 LTS / Godot 4.5.2 unless explicitly marked otherwise. R5 compilation,
R3/R6 review by the same agent. These are scoped findings, not universal rules.

## Oversized character

**Verified finding:** evaluated masked skin was 2.430801340 m despite metre units;
this was not just a display-unit issue. The original cause of that size is unknown.
**Confirmed correction:** normalise mesh data, every shape-key block and armature
rest data together to the task's 1.80 m target; preserve original source.
**Regression:** evaluated skin bounds, hierarchy/transforms, shape keys and export.
[Evidence](../HUMAN_SCALE_REVIEW.md). Do not use head-bone tail as stature.

## Stiff push-off / source and GLB anchors disagree

**Verified finding:** the first toe-tip candidate used a Blender bone tail, which
was not preserved as the same endpoint through GLB. Held/zero-speed foot rotation
also made the release read stiff in the reviewed pass.
**Confirmed approach:** explicit foot/toe pose phases and slopes, ankle compensation
around heel/ball/sole-tip anchors; select the low front sole from each mesh.
**Regression:** contact drift including travel, actual skin height, loop and knee
continuity. Selection bands and anchors are model-specific.
[Evidence](../WALK_PUSHOFF_REVIEW.md).

## Dip reads as a limp

**Verified measurement:** the reviewed vertical cycle was symmetric to 0.00012 mm.
**Working diagnosis then:** prolonged low pose followed by abrupt rise/descent,
rather than left/right asymmetry. A symmetry check alone did not establish feel.
**Correction:** shallower, shorter settling with a continuous rise/fall. Later
landing work superseded those exact height values.
[Historical dip review](../WALK_DIP_REVIEW.md); [successor](../WALK_KNEE_REVIEW.md).

## Knee wobble / snap near contact

**Verified finding:** the sampled knee bend plane stayed forward, while extension
reversed into loading too rapidly. Moving the bend plane was not justified by that
measurement. Soft reach corrections can themselves create sudden changes when
switching on, or leave a residual offset at touchdown.
**Confirmed approach:** match late-swing flexion/velocity into contact, release
correction offsets smoothly and check cyclic second differences across joins.
For Run, continuous recovery curves, support-height planning and matching airborne
recovery to the actual support pose replaced abrupt reach corrections.
**Regression:** authored and half-frame knee measurements, loop and both lead joins.
Walk and Run limits differ; use their task-local tests, not one universal threshold.
[Walk evidence](../WALK_KNEE_REVIEW.md), [run implementation](../../tools/blender/build_run.py),
[run results](../RUN_REVIEW.md).

## Chest surges when leaving Idle

**Verified finding:** no instantaneous pose jump, but the actual 0.12 s Godot blend
produced 1.061 m/s early chest speed. The authored 2.5-degree lean reached full
amount in 0.18 s, alongside 12 mm hip translation over 0.12 s.
**Confirmed correction:** 1.25-degree lean, onset 0.06 s and rise 0.30 s, following
6 mm hip lead over 0.20 s. Early chest speed fell to 0.189 m/s (82% reduction).
**Regression:** spine01 through real playback from four Idle phases, not just
smooth source curves. [Evidence and before/after](../WALK_START_CHEST_REVIEW.md).

## Source clothing looks acceptable but exported run intersects

**Verified finding:** early run exports intersected at the centre-front crotch,
including up to about 3.8 mm vertex penetration; some source samples appeared clear.
The source has post-armature Smooth/Solidify modifiers. Attribution of every
export difference to one modifier is not established by those observations.
**Unsuccessful trials:** excessive high-knee recovery, greater local front inflation,
and one linear subdivision did not resolve all folding; subdivision was removed.
Do not repeat subdivision as a proven fix for this case.
**Confirmed combined correction:** earlier recovery behind the body, unfolding
before landing, smooth support and toe clearance, and up to 8 mm local front-seam
ease in v0.3. Original topology retained; final new-clip body/cloth and cloth-self
intersection counts zero. Older clips received 155 body/cloth-clearance samples.
The final combined result does not isolate the causal contribution of each change.
**Regression:** test exported mesh, all affected new clips and retained clips.
[Evidence](../RUN_REVIEW.md), [validator](../../tools/blender/test_run.py).

## Preservation checks and scale state

**Verified in chest pass:** regenerated stop quaternion components differed by
1.125e-6 against a 1e-6 cutoff. The validator retained component diagnostics and
added an every-authored-pose skinned-surface comparison with a 0.01 mm limit.
The largest preserved Idle/stop surface difference was 0.001795 mm.
This was a documented measurement change, not proof that every numeric mismatch
is harmless. [Evidence](../WALK_START_CHEST_REVIEW.md).

**Verified in run pass:** exporting with Run active changed unkeyed Idle scale
channels by about 4e-6. Restoring the predecessor's active Idle export state made
all five predecessor action channels match exactly. The v0.3 file is saved with
Run selected; the generator then selects Idle for export. Preserve that distinction.
[Implementation](../../tools/blender/build_run.py), [preservation report](../../tools/blender/locomotion_v03/validation.json).

## Right-lead metadata accidentally becomes phase zero

**Verified defect during run development:** a temporary root-height variable reused
`offset`, overwriting the right-lead phase in build metadata while poses remained
right-led. Endpoint tests caught approximately 0.54/0.83 m mismatches.
**Confirmed fix:** separate `height_offset` from lead phase. L = 0, R = 0.5.
**Regression:** both lead endpoint surfaces and runtime lead-selection cases, not
just left-lead previews. Final maximum endpoint mismatch is about 0.001208 mm.
[Generator](../../tools/blender/build_run.py), [tests](../../prototype/tests/test_run.gd).

## Preview dependency / text encoding

**Verified incidents:** a new shell lacked the preview Pillow PYTHONPATH; packaging
failed until the existing preview dependency was supplied. A document written using
the Windows default encoding failed UTF-8 checks; naive newline conversion also
introduced extra blank lines.
**Practice:** explicitly select dependency environment and UTF-8/newline policy.
Validate media frame counts/durations and document links after packaging. These
are environment-specific lessons; temporary dependency paths are not portable.

## MCP connection troubleshooting: incomplete history

Read-only live inspection succeeded on 9 November 2026. The user supplied guidance
from another chat about documenting its connection troubleshooting, but not the
underlying diagnostic transcript. Earlier connection symptoms/root causes/fixes
remain unverified here. Do not manufacture a connection recipe from that summary.

## Runtime gait blends penetrate the floor

**Verified in motion demo v0.4:** individually valid v0.3 clips produced up to
8.665 mm sampled sole penetration when combined at runtime. Source validation
does not certify arbitrary runtime blends. A model-specific root-height correction
uses exported foot skin vertices/weights; sampled full-body bounds then reached
only -0.000000133 m (float noise), with at most 9.961 mm correction in the rehearsal.
**Limits:** no X/Z contact locking, IK or source edits; sharp-turn pivoting and
runtime cloth collision remain separate questions. Preserve source hashes and
retest the full skin after changing probe selection. [Evidence](../MOTION_DEMO_V04.md).

## Narrow motion cannot blend directly to wide idle without foot drift

**Verified in this human's stop generator:** only the trailing foot lifts during
WalkStopL/R; the leading foot remains planted. Narrowing both moving feet and
cross-fading straight to wide Idle would require the support foot to move sideways.
**Implemented:** retain lateral placement per foot, widen the trailing foot during
its existing recovery, then give the leading foot a small outward settling step.
Keep corrections interruptible, capped in speed and attached to swing timing.
The runtime leg solve preserves source foot orientation and knee bend plane.
**Checks:** both leads/eight release phases, restarts during settling, actual sole
height while lateral correction changes, body/garment geometry and three views.
[Evidence](../STANCE_REVIEW.md). This model-specific adapter is not a universal rig rule.

## Entry template

Record symptom; model/export/version; verified measurements; working diagnosis;
failed trials; confirmed fix; reproduction/checks; evidence paths; scope and
remaining uncertainty. Update the model/work log when the fix changes a contract.

## Kevin Iglesias dummy: native bake versus FBX — 9 November 2026

Scope is Basic Motions FREE 2.4 male dummy, Blender 5.2.3 and Godot 4.5.2.
The first FBX trial showed greater sampled between-frame sole penetration than
the native-source bake. Quaternion sign correction changed zero keys, so that
hypothesis was not confirmed. Native evaluated-source export passed surface
preservation, repeat-hash and Godot floor tests. Set quaternion rotation mode
before assigning baked matrix_basis. Details, source hand-control warnings
and remaining limitations: [test 01 record](../../tools/kevin_walk/README.md).
This is not a universal judgement about the publisher's FBX files.

## Dummy Idle01 needs source evaluation priming

Verified for Kevin Iglesias Basic Motions FREE 2.4 in Blender 5.2.3:
selecting Idle01 then sampling its first frame immediately retained stale
constraint state and failed surface preservation by 0.891 m. Evaluating the
loop end and beginning first resolved that initial state; the final closed
bake differs by at most 1.044 mm and repeats to the same GLB hash.
[Test 02 evidence](../../tools/kevin_locomotion/README.md).
Retain Godot-generated import metadata on subsequent clip builds and run editor
import before launching the game; a stale generated cache path is not a rig fault.

## Kevin multi-pack action viewer (Blender 5.2.3 / Godot 4.5.2)

Verified in the Prototype 02 test-03 [execution record](../../tools/kevin_actions/README.md):
Godot's name-suffix import processing strips _Loop and broke five exact catalogue
IDs. Set nodes/use_name_suffixes=false for these packs. Native padded action
frame ranges are not clip boundaries; FBX Take/LocalTime ticks provide durations.
Three-point floor sampling missed the in-place jump dip; 60 Hz source skin minima
plus a measured 4 mm import/interpolation allowance passed the final 113-entry
sampled floor check. This is not a universal floor margin.

The supplied arrow's +Z shaft maps into the right hand-prop socket with -90
degrees around X; +90 pointed it backwards. Separate bow-rig bones and a visible
string are baked onto the preview rig. Hand-only swords do not remain sheathed;
viewer prop bones transfer them to a back mount. Keep these adapters separate
from any future inventory or production equipment implementation.

## Open P02-ARCHERY-01: owner-reported firing defect

The 9 November owner recording shows an unacceptable arrow-firing presentation;
sampled frames can show the arrow detached/misaligned. The exact cause and clip
phase have not been isolated. Verified: current code hides a hand-attached arrow
on a fixed delay and has no projectile flight. Earlier orientation and static
pose fixes do not resolve or validate this. See the [checkpoint issue](../PROTOTYPE_02_CHECKPOINT.md#p02-archery-01--arrow-firing-open)
for evidence, scope and future checks. Left open at the owner's requested checkpoint.
