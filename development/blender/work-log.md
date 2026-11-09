# Blender work log and continuation state

Last updated: 9 November 2026. Current accepted checkpoint: v0.3, `5161379`,
`human_male_prototype_v0.3`. Existing branch: human-prototype-01 in Gauntlands.

| Stage | Durable evidence | State |
| --- | --- | --- |
| Model scale and underwear | [Scale](../HUMAN_SCALE_REVIEW.md), [briefs](../BRIEFS_V2_REVIEW.md) | Historical verified preparation |
| Walk feel iterations | [Locomotion](../LOCOMOTION_REVIEW.md), [push-off](../WALK_PUSHOFF_REVIEW.md), [dip](../WALK_DIP_REVIEW.md), [knees](../WALK_KNEE_REVIEW.md), [upper body](../WALK_UPPER_BODY_REVIEW.md) | Historical passes; current values live in frozen v0.1 generator |
| v0.1 walk | [Approval](../HUMAN_MALE_PROTOTYPE_V01.md) | Accepted; f4579d0 |
| v0.2 Idle/start/stop | [First slice](../HUMAN_MALE_PROTOTYPE_V02.md), [chest correction](../WALK_START_CHEST_REVIEW.md) | Accepted; 12b2b0b |
| v0.3 Run/gait changes | [Run review](../RUN_REVIEW.md), [model contract](models/human-male-prototype.md) | Accepted; 5161379 |
| v0.4 motion demo | [Scope, implementation and evidence](../MOTION_DEMO_V04.md) | Implemented for owner feel review; dedicated turn clips remain unimplemented |

The full series of WALK_*_REVIEW.md files in development remains the detailed
history. Their own superseded/current notices take precedence over old measurements.
No old review is silently promoted into a current rule by being linked here.

## Latest production handoff

Approved: relaxed unarmed locomotion source/export and review pipeline. v0.3 passes
Blender export checks and Godot 30/60/120 Hz transition tests; the owner approved
its feel and requested its commit. Original v0.1/v0.2 manifests remain preserved.
The latest checkpoint import/test rerun passed before commit. See the run review
for exact commands, limits, counts, captures and known restrictions.

## Moving stance / return to idle — 9 November 2026

User requested inward moving landings and a wide idle, explicitly including the
transition back to idle. R3 lead; R2/R6 same-agent integration and checks. Baseline
7bbeff5. [Full record](../STANCE_REVIEW.md) covers the runtime two-bone stance adapter,
20 mm inward placement per foot, trailing-foot recovery then leading-foot settling,
interruption safeguards and actual results. Frozen Blender source/exports retained.
Stance, motion and run-up suites pass; sixteen sampled body/garment pairs are clear.
Three-view rendered poses reviewed; owner feel approval remains pending.

## Run-up pass — 9 November 2026

User requested at least a clear walking step before running. R2 lead with same-agent
R3/R6 review. Baseline 69e9ea7. [Full record](../RUN_UP_REVIEW.md) names changed code,
commands, timing, captures and limitations. From rest, first travelling step ends
at 1.30 s, Run begins blending around 1.43 s and reaches full speed around 1.85 s.
Release and steering remain interruptible; established walking keeps its phase.
Import, focused run-up suite and full motion regression pass. Three-view rendered
poses reviewed. Owner feel approval and physical-controller testing remain pending.
No source asset or stance-width change. Replay test now demonstrates this lead-up.

## Motion demo pass — 9 November 2026

User authorised the proposed joypad/motion demo. R2 lead; R3/R6 reviewed interfaces
and evidence in the same agent. [Full record](../MOTION_DEMO_V04.md) names files,
commands, failed floor-clearance trial, correction, tests, previews and risks.
F5 now opens motion_demo.tscn; prior review scenes and frozen assets are retained.
Simulation and visual state are separate; controls follow the approved analogue
left-stick mapping. Three-view playback and repeatable rehearsal are available.
Import, motion tests, 16 phase-stop cases, 24 direction/camera cases and existing
v0.3 regression pass. Rendered samples reviewed in all three views. Live XInput
detection verified; physical controller movement/feel and owner acceptance pending.
No v0.4 approved checkpoint/tag yet. Next owner is the user for feel review, then
R2/R3 for targeted turning/stop refinement; no equipment/combat scope added.
During handoff the owner identified moving stance width versus resting stance.
The source uses nominal +/-0.125 m ankle tracks across Idle/Walk/Run; a narrower
moving track and wider/slightly staggered resting stance are recorded as the
[next polish candidate](../MOTION_DEMO_V04.md#owner-observation-during-demo-handoff).
No stance-width source edit was included in this pass.

## Documentation pass — 9 November 2026

Request: record work durably and establish shared Blender knowledge across chats.
R5 lead; R3/R6 review by the same agent. Added playbook, model contract,
troubleshooting and this log; linked mandatory read/update rules from AGENTS.md.
Inspected existing reviews/scripts/reports and performed a read-only live Blender
inventory: v0.3, Blender 5.2.3 LTS, 137 bones, ten actions, nine body shape keys,
two packed textures, no pose-bone constraints. No asset, animation or gameplay
change. Earlier MCP connection troubleshooting from the other chat was not supplied
and remains explicitly unverified. No cross-project skill created.

Validation for this documentation change: local relative links, referenced
checkpoint commits, frozen manifest hashes and diff whitespace. No Godot/Blender
build or animation test rerun is needed for text-only changes; earlier production
checks are cited, not represented as newly executed.

## Record format for subsequent work

Date/request; owner and reviewers; baseline commit/hash; changed artifact paths;
interface/timing changes; commands actually run and pass/fail/not-run evidence;
visual review versus owner acceptance; failed trials and linked lessons; current
commit/tag and pending work. Keep unrelated user changes out of scoped commits.

## Prototype 02 dummy walk test — 9 November 2026

Owner authorised the male dummy, one forward walk, flat floor, joypad movement
and three cameras. Branch human-prototype-02; R2 lead, same-agent R3/R6 checks.
[Full record](../../tools/kevin_walk/README.md) and
[model interface](models/kevin-male-dummy.md) contain sources, licence, hashes,
commands, results, failed attempts and limitations. F5 launches dummy_walk.tscn.
Repeat export matched; Godot import, 72 travel cases and 97 floor samples pass.
All six rendered pose/facing sheets inspected. Physical joypad operation and
owner feel approval remain pending. Prototype 01 and source downloads unchanged.

Owner approved dummy walk test 01 as perfect on 9 November 2026. Next authorised
slice: idle and run/walk transitions, explicitly excluding sprint.

## Prototype 02 idle/run pass — 9 November 2026

Approved walk saved as 426f7e2. Owner requested run/walk and idle, no sprint.
R2 lead with same-agent R3/R6 review. [Test 02 record](../../tools/kevin_locomotion/README.md)
contains source ranges, hashes, reproducible builds, blend timing, actual checks,
source idle evaluation fix, import-cache failure and remaining limits.
F5 opens the new dummy_locomotion.tscn; the approved walk scene/GLB are unchanged.
Idle and 4 m/s Run are added, with shared walk/run phase and three review views.
Physical controller operation and owner feel approval remain pending.

## Prototype 02 animation viewer — 9 November 2026

Owner approved idle/walk/run as excellent and requested joypad action playback,
LB/RB or dropdown selection, matching weapons and as many available animations
as practical. Subsequent instruction explicitly adds sprint to selection only.
R2 lead; same-agent R3/R6 work. Baseline walk commit 426f7e2 plus the approved
uncommitted test-02 files; those locomotion scripts/exports are preserved.

Added dummy_actions scene/script, action_catalogue, builder, tests/capture tooling
and [full execution record](../../tools/kevin_actions/README.md). Five native packs
provide 113 selectable entries with sword, shield, polearm, bow and crafting
props. No gameplay combat or v3 work. Headless editor import, 113-entry
validation, actual synthetic Godot input dispatch and locomotion regression pass.
Rendered and inspected all 15 catalogue sheets, 11 sequences and three eight-facing
sheets across the three cameras (675 rendered frames).

Resolved suffix-based missing clips, insufficient floor samples, reversed arrow
and hand-only sheathing; scope and measured corrections are recorded in the
README and troubleshooting. Physical controller operation, normal-speed owner
feel approval and a fresh whole-catalogue repeat-build remain unverified.
Licensed generated assets remain local/gitignored. No push or merge performed.
Final handoff checks: documentation links and git diff --check passed; Walk,
Idle and Run GLB SHA-256 hashes still match the approved test-02 exports.
Only incidental import-file rewrites from this run were restored. The completed
viewer launched in the owned Prototype 02 Godot process with a visible window
and no startup errors. Other projects/editors were left alone. Work remains
local on human-prototype-02; this pass made no commit, push or merge.

## Owner acceptance and checkpoint commit — 9 November 2026

Owner: viewer was great except arrow firing; resources are sufficient for initial
prototype game structures. Explicit request: document and commit all work to this
stage. R5 lead, same-agent R6 verification; no animation/code fix in this pass.
[Checkpoint](../PROTOTYPE_02_CHECKPOINT.md) records accepted scope, preserved
artifacts, reproduction dependencies, v3 boundary and open P02-ARCHERY-01.

Reviewed 12 sampled frames from the supplied 24-second recording using background
Blender VSE. Saved a review sheet and video hash/metadata; preserved a local full
copy. Arrow presentation can appear detached/misaligned; exact cause/timing is
unverified. Code inspection confirms fixed-delay hiding and no projectile flight.
The earlier orientation correction is not sign-off of firing. No arrow fix was
attempted. Owner acceptance now supersedes historical pending resource-review
notes, while archery remains an explicit exception.

Checkpoint verification: Godot headless editor import, all 113 action tests and
locomotion regression passed again. Documentation links and approved export
hashes passed. [Machine-readable checkpoint evidence](../../tools/kevin_actions/checkpoint_validation.json).
This checkpoint includes the approved locomotion and animation-viewer code,
builders, manifests, rendered evidence and documentation. Licensed source/export
assets and the full owner video remain local. No push or merge.
The initial checkpoint import exited successfully but logged get_multiple_md5
file-hash diagnostics while refreshing historical Prototype 01 texture imports.
A second editor import completed with no ERROR/WARNING entries. This was an
import-cache refresh observation; no historical source assets were changed.
