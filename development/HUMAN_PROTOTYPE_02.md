# Human Prototype 02 — Kevin Iglesias asset trial

Recorded: 9 November 2026.
Primary owner for setup: R5, Pipeline & DevOps Engineer.
Review: setup self-check only; no independent art or runtime review performed.

## Authorisation and starting point

The owner requested a new branch named `human-prototype-02` as the test area
for Kevin Iglesias models, following the decision to evaluate free assets
before considering paid packs.

- Repository: https://github.com/Jonty303/Gauntlands
- Branch: `human-prototype-02`
- Local checkout: `S:/OneDrive/__Github/Gauntlands-human-prototype-02`
- Base: `human-prototype-01` at `bd26fc05bce851f4fa8398badec0b439074ab2cf`
  (Narrow moving foot placement and settle back to wide idle).
- Original checkout: `S:/OneDrive/__Github/Gauntlands`, still on
  `human-prototype-01`. Its existing uncommitted work remains there.
- The unfinished v0.4 fast-run changes and draft speed plan are not included
  in this branch's committed base.

This explicit authorisation overrides historical instructions limiting work
to Prototype 01. The separate Project-Gauntlands archive is not part of this
trial. No merge, push or purchase is authorised by this setup.

## Local source assets — verified inventory only

Owner-supplied files are at `S:/OneDrive/__Github/Human`.
They remain external to the repository; no assets were copied or imported.

The directory contains FBX models and animations, plus these pack documents:

- Human Basic Motions 2.4 FREE.pdf
- Human Archer Animations 2.0 FREE.pdf
- Human Crafting Animations 2.2 FREE.pdf
- Human Melee Animations 2.0 FREE.pdf
- Human Spellcasting Animations 2.0 FREE.pdf

Blender source archives for all five packs were found under `Animations/`,
including `HumanBasicMotionsFREE_BlenderFiles.zip`; a dummy model source
archive was found under `Models/HumanDummyModels_Source.zip`.

Publisher: https://www.keviniglesias.com/
Basic Motions source: https://kevdev.itch.io/basic-motions-free

Names and locations are verified, not archive integrity, licence clearance,
rig compatibility or motion quality. Review the supplied licence and record
source hashes before importing selected assets or committing third-party files.

## Proposed first evaluation

Keep the first trial bounded to idle, walk, run and sprint. Establish a
reference on the supplied character, then assess retargeting onto our human.
Reuse Godot 4.5.2 and the existing motion demo where appropriate.

Acceptance for animation work remains pending:

- Repeatable import/retarget/export with documented rig, units and facing.
- Fluid transitions and acceleration; no foot sliding or abrupt knee snaps.
- Review in isometric, raised 3/4 and top-down views, with eight facings.
- Compare against the existing prototype before replacing accepted motions.
- Record controller tests separately from headless import checks.

This branch setup does not claim that these evaluation steps have been run.

## Setup evidence

- Inspected repository instructions, remote, local branches and working tree.
- `git ls-remote --heads origin human-prototype-01 human-prototype-02`
  found Prototype 01 at the base above and no remote Prototype 02.
- `git worktree add -b human-prototype-02 S:/OneDrive/__Github/Gauntlands-human-prototype-02 human-prototype-01`
  succeeded; the new checkout initially had a clean working tree.
- Added this record and the scoped authorisation note in `AGENTS.md`.
- No code, scene, import or animation changes; Godot/Blender execution is not
  applicable to branch setup. Asset and gameplay acceptance remain unverified.

## First test implementation — 9 November 2026

Owner narrowed and authorised test 01 to the male dummy and one forward walk.
[Test record](../tools/kevin_walk/README.md) contains the local setup, commands,
validation and review limits. F5 launches it. The broader idle/run/sprint and
retargeting evaluation above remains proposed.

## Test 02: idle and run/walk

Owner accepted the dummy walk and authorised adding idle and run/walk, excluding
sprint. [Implementation and evidence](../tools/kevin_locomotion/README.md).
The first test is checkpointed at 426f7e2; F5 now opens the separate second test.

## Test 03: selectable animation viewer

Owner approved test 02 as excellent, then authorised an animation viewer before
retiring Prototype 02. The later instruction allows sprint only as a selectable
preview; joystick locomotion still ends at Run, 4 m/s.

F5 now opens dummy_actions.tscn: 113 entries from all five supplied human packs,
A to play, LB/RB or dropdown to select, B to return, appropriate action props,
and the three review cameras. [Build, controls and evidence](../tools/kevin_actions/README.md).
This is a motion viewer, not combat/inventory implementation or v3.
Automated checks and sampled three-view review pass; owner feel/controller
acceptance remains pending. No push or merge is authorised by this pass.

## Resource evaluation accepted — checkpoint

On 9 November 2026 the owner confirmed that the resources are sufficient for the
initial prototype game structures and authorised committing the work to date.
The animation demo was accepted with an explicit arrow-firing exception.
[Checkpoint and open issue P02-ARCHERY-01](PROTOTYPE_02_CHECKPOINT.md) are the
current acceptance/handoff record. Earlier pending notes are historical.
