# Blender playbook

Last reviewed: 9 November 2026. R5 documentation lead; R3/R6 evidence review by
the same agent. Scope: Jonty303/Gauntlands, existing human-prototype-01 branch.
This is a navigation and practice record; it does not authorise new production.

## Start here

Read the repository [AGENTS.md](../../AGENTS.md), this playbook, the relevant
[model record](models/human-male-prototype.md), and [troubleshooting](troubleshooting.md)
before modelling, rigging, animation, export or Blender connection work.
Use the [work log](work-log.md) to identify the latest accepted checkpoint.
The original detailed reviews remain evidence; do not replace them with summaries.

Verify checkout/branch and existing changes first. This project's repository is
`S:/OneDrive/__Github/Gauntlands`. The similarly named `Project-Gauntlands` checkout
is a separate archive. A chat's current directory is not proof of project identity.

## Evidence language

- **Verified:** supported by an inspected asset/script, saved report, executed check
  or explicit owner decision. Give date, asset/version and a relative evidence link.
- **Working diagnosis:** plausible explanation with incomplete causal evidence.
- **Unverified:** not measured or not reproduced in the relevant environment.
- **Superseded:** a historical result, not the current parameter or contract.

A fix verified for this human is not a universal recipe. Record unsuccessful trials
and what actually failed. Do not rewrite historical measurements as current results.
Temporary backups/logs help recovery but are not the durable evidence store.

## Authoring and iteration practice

1. Name the owner/review roles, bounded change, baseline and observable acceptance.
2. Preserve accepted source/export/generator hashes. Build a versioned derivative;
   use manifest files and Git checkpoints rather than overwriting an accepted asset.
3. Put motion changes into reproducible scripts. Treat saved Blender UI edits as
   provisional until recorded in the authoring path or explicitly documented.
4. Define contact phases, travel and coordinate conventions together. Check ankle,
   toe and actual skinned sole separately. Bone tails are not a portable GLB anchor.
5. Measure motion through the actual runtime blend as well as the authored action.
   Smooth curves alone do not establish smooth perceived movement.
6. Inspect geometry after export. Source modifiers/skin evaluation do not certify
   exported clothing clearance. Retest older clips after a shared garment change.
7. Keep runtime movement/state intent separate from authored visual clips. The
   current review viewer's queued transitions are not approved gameplay latency.

These practices are grounded in the human prototype evidence linked below; numeric
settings and the analytic IK solver remain specific to that model.

## Validation and review

Use the model's current scripts and reproduction commands. Narrow checks first;
run export and Godot regression when assets or runtime behaviour change. Check
loop/transition positions AND knee velocities/second differences, contact drift,
floor clearance, clothing and hand intersections, preservation and report hashes.
Document new task-local limits before evaluating; do not change them to hide a fault.
If a measurement itself is defective, explain and retain the prior result.

Always distinguish: source inspection, exported checks, engine checks, sampled
visual review, normal-speed owner approval, and actual controller testing.
The [three-view contract](../HUMAN_MODEL_REVIEW.md) requires isometric, raised 3/4
and top-down plus eight-facing poses. Match cameras, scale and elapsed times for
comparisons. Top-down cannot alone establish foot height or knee clearance.

## Tool and data discipline

Verified here: Blender 5.2.3 LTS, Godot 4.5.2 stable. Installation-specific executable
paths live in the [environment reference](../TARGET_DEVELOPMENT_ENVIRONMENT.md)
and task execution records; check availability rather than assuming PATH entries.
The encoder uses Pillow. Shell environments may not inherit its temporary-library
PYTHONPATH. Use explicit UTF-8 and consistent newlines for new text files.

Before operating live Blender, inspect its file and dirty state. Prefer read-only
inventory first; do not discard unknown user edits. Action slots are used in this
Blender version; the scripts assign both action and action_slot. Source animation
starts at frame 1; the GLB export slides clips to zero. Those are this pipeline's
conventions, not all Blender workflows.

The live MCP connection was successfully used for read-only inventory on
9 November 2026. Earlier connection-troubleshooting details from another chat
have not been reviewed here; do not invent installation steps, ports or fixes.
A future cross-project skill may extract verified reusable practices. No such
skill has been created or installed by this documentation task.

## Required update after each pass

Update the work log with request, exact baseline, changed paths, verified checks,
results, owner decision and remaining work. Update the model record for interface
changes; add a troubleshooting entry for a reusable diagnosis or failed approach.
Keep current state and historical evidence distinct. Record commit/tag when made;
never imply a local checkpoint was pushed or another chat has read these files.
