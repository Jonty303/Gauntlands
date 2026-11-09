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
| Turning / joypad demo | User requested this as the next development direction; proposal below | Not implemented |

The full series of WALK_*_REVIEW.md files in development remains the detailed
history. Their own superseded/current notices take precedence over old measurements.
No old review is silently promoted into a current rule by being linked here.

## Latest production handoff

Approved: relaxed unarmed locomotion source/export and review pipeline. v0.3 passes
Blender export checks and Godot 30/60/120 Hz transition tests; the owner approved
its feel and requested its commit. Original v0.1/v0.2 manifests remain preserved.
The latest checkpoint import/test rerun passed before commit. See the run review
for exact commands, limits, counts, captures and known restrictions.

Next proposed slice: a flat-area joypad demo, camera-relative steering, walking
and running intent, then planted-foot turns. Initial discussion suggested analog
walk/run selection, tighter walking turns, wider running turns and 90-degree turns
before 180-degree reversals. These are proposed controls/design choices, not
implemented or separately accepted parameter values. Write the bounded movement
brief before code. R2 would lead; R3 would own required turning animation.
The existing contact-wait/whole-clip queue is a review tool, not the responsiveness
contract for gameplay. Direct sprint starts/stops and equipment remain separate.

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
