# Prototype 02 checkpoint — 9 November 2026

## Owner decision

The owner reviewed the animation viewer and said it was great, apart from arrow
firing. They confirmed that the available model and animation resources are
sufficient for the initial prototype game structures and requested this commit.

**Accepted:** the resource-evaluation milestone, the dummy walk, idle/walk/run
trial, and the broad animation-selection demonstration. **Open exception:**
P02-ARCHERY-01, arrow-firing presentation. This is not acceptance of production
combat, every animation's final polish, or the current arrow release.
No v3 implementation, branch creation, push or merge is part of this checkpoint.

## What is preserved

- Approved dummy walk checkpoint 426f7e2, with its source/export validation.
- Idle / walk / run test: native clips, shared walk/run phase, acceleration,
  first walking step, return to idle, joypad/keyboard controls and three cameras.
- Animation viewer: **113 selections** (112 unique supplied clips plus a complete
  bow sequence), A/Space to play, LB/RB or dropdown to select, B/Esc to return.
- Sword, shield, greatsword, polearm, bow/arrow and crafting props. Sprint is
  **selector-only**; ordinary movement still tops out at Run, 4 m/s.
- Reproducible Blender builders, source/export hashes, Godot tests, review
  manifests, 15 catalogue sheets, 11 sequence sheets and three facing sheets.
- Prior procedural-human work and lessons remain preserved in this branch's
  history and [Blender records](blender/models/human-male-prototype.md). This
  checkpoint does not alter the separate Prototype 01 worktree.

Current launch scene: [dummy_actions.tscn](../prototype/dummy_actions.tscn).
Open [project.godot](../prototype/project.godot) in Godot 4.5.2 and press F5.
The earlier walk and locomotion scenes remain available independently.

## Reproduction and evidence

- [Walk test and licensed-source setup](../tools/kevin_walk/README.md)
- [Idle/walk/run build and validation](../tools/kevin_locomotion/README.md)
- [Action viewer: controls, build, interfaces and checks](../tools/kevin_actions/README.md)
- [Action validation](../tools/kevin_actions/validation.json)
- [Locomotion validation](../tools/kevin_locomotion/validation.json)
- [Model interface](blender/models/kevin-male-dummy.md)
- [Chronological work log](blender/work-log.md)

Blender 5.2.3 LTS and Godot 4.5.2 were used. Native source downloads are under
S:/OneDrive/__Github/Human; the downloaded dwarf assets remain available under
S:/OneDrive/__Github/Dwarf but were not integrated by this trial. Source files and
derived standalone models/animation GLBs stay local and gitignored under the
publisher's licence. The commit includes the builders, manifests and rendered
review evidence, not the licensed source packs. A fresh checkout therefore needs
the licensed downloads and documented asset builds before it can run.

Before this checkpoint commit, the Godot headless editor import,
test_dummy_actions.gd (113 entries) and test_dummy_locomotion.gd all passed.
The completed results are recorded in the linked JSON reports. Automated checks do not cover projectile trajectories, nock alignment
through the whole shot, weapon collision or subjective feel. The owner review
supersedes the earlier pending-approval notes for resource sufficiency, while the
agent's own physical-controller test remains not performed.

## P02-ARCHERY-01 — arrow firing (open)

Owner evidence: 20261109-1955-27.3039084.mp4, 24 seconds, 30 fps, 472 x 378.
[Review sheet](../tools/kevin_actions/owner_arrow_review.jpg) and
[source hash/metadata](../tools/kevin_actions/owner_arrow_report.json) preserve
traceability. A copy of the full recording is retained locally at
.local/kevin/owner_video/source.mp4; it is not required to run the project.

Observed in sampled frames: the bow action plays, but arrow presentation can
look detached/misaligned during the shot (for example around 6.54 s). The owner
explicitly rejected the firing result. Exact clip timing and the full cause have
not been isolated; the cropped recording does not identify the selected entry.

Verified implementation limitation: the arrow remains a hand-attached preview
prop and is hidden on a fixed delay, 0.1 s into Release or after the complete-shot
release marker. There is no independent flying projectile. Earlier checks fixed
its reversed orientation and reviewed sampled poses, but did not establish a
correct firing sequence. Their pass must not be interpreted as archery sign-off.

Future owning roles: R3 + R2, reviewed by R6. Before production archery, inspect
load/hold/release at normal and slow speed from side, 3/4 and top-down views;
align arrow nock, drawing hand, bowstring and aim axis; establish the actual
release frame. If gameplay shooting is then authorised, transfer the arrow to
an independently moving projectile at release rather than hiding it on a timer.
Cover all eight facings and interrupted/repeated actions. No fix was attempted
in this documentation-and-commit pass.

## Boundary for the next stage

Prototype 02 answers whether the supplied resources are adequate to proceed.
The answer is yes, per the owner. Define and authorise v3 separately: its game
structures, chosen character appearance, equipment rules and required actions.
Retargeting, armour/clothing, other races, combat timings, damage and projectile
behaviour are not already proven by this viewer.
