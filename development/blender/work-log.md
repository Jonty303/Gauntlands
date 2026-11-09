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
