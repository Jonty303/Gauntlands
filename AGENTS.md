# Gauntlands — repository agent instructions

## Authorised Prototype 02 exception — 9 November 2026

The owner explicitly authorised `human-prototype-02` as the test area for Kevin
Iglesias models and animations. On this branch, that authorisation supersedes
the older single-branch restriction below and in the development instruction
documents. It does not authorise merges, pushes, purchases or wider gameplay.
Read [the trial record](development/HUMAN_PROTOTYPE_02.md) for the starting
checkpoint, local asset location, scope and pending validation.


This file is the **Codex and repository-working entrypoint**. Read the detailed [agent role register](development/AGENT_ROLES.md), [operating model](development/AGENT_OPERATING_MODEL.md), [project instructions](development/PROJECT_CUSTOM_INSTRUCTIONS.md) and [environment reference](development/TARGET_DEVELOPMENT_ENVIRONMENT.md) before substantial work.

## Identity and source control

- This repository is **Jonty303/Gauntlands**. Never use, modify or import from `Jonty303/Project-Gauntlands-Archive` or the owner's separate private Gold Box-style RPG unless explicitly authorised.
- Treat `main` as protected. Documentation/configuration records may be added there **only when expressly authorised**; no gameplay prototypes, Blender production assets or Godot implementation on `main` by default.
- The first underwear-only human prototype belongs on a **single** branch named `human-prototype-01`, created from `main` **only when explicitly authorised**. Do not create other branches, branch-producing worktrees or merges before explicit approval of that human. Do not silently create `human-prototype-01` if absent.
- Do not merge to `main`, force-push, delete work or modify unrelated files without explicit permission.
- Before edits verify `git remote -v`, `git status --short --branch`, remote branch existence, current spec and any uncommitted work; preserve the user's changes.

## Operating contract

- Choose one primary role among L0–R6 defined in `development/AGENT_ROLES.md`; name any reviewers.
- Design before implementation: identify approved references, in/out of scope, dependencies and **observable** acceptance criteria.
- Prefer small testable slices and reuse; do not implement Stage 02 weapons or full gameplay systems during human Prototype 01.
- Record exactly what was edited and **which** commands/tests were run with their results. Never claim Blender/Godot visual or controller validation from headless checks alone.
- Pin tools only after verified installation. Godot's current documented baseline is **4.5.2 stable**; Blender/MPFB exact versions are not yet pinned.
- Put durable configuration, tooling and troubleshooting records in `development/` and distinguish target state from tested state.
- Avoid credentials, tokens and secrets in source or documentation. Respect approved third-party asset licences.

## Current narrow prototype boundary

One believable underwear-only human; reusable modelling/rigging/animation pipeline; single flat Godot test plane; eight-direction walking. No other prototypes, branches or merges until the first human is explicitly approved.

The approved first-playable scope, weapon roadmap and reuse principles live in `encyclopedia/design reference/` (see its `README.md`). They are **not** authorisation to build the five-class release during Prototype 01. Future unapproved proposals belong in `drafts/`.


## Blender knowledge and work recording

- Before modelling, rigging, animation, Blender export/import or connection troubleshooting,
  read the [Blender playbook](development/blender/playbook.md), the applicable
  [model record](development/blender/models/human-male-prototype.md), and
  [troubleshooting](development/blender/troubleshooting.md). Check the
  [work log](development/blender/work-log.md) for the latest accepted baseline.
- After each relevant pass, update the work log and affected model/lesson records.
  Record artifact paths/revisions, commands actually run, results, failed attempts,
  remaining risks and owner approval separately from technical validation.
- Label verified findings, working diagnoses, unverified assumptions and superseded
  results. Include model/tool-version scope and evidence links; do not generalise a
  workaround for this human to other assets without testing it.
- Keep historical review records and frozen manifests. Chat history or temporary
  files alone are not a durable handoff. This documentation requirement does not
  expand production scope or authorise a push, merge, new branch or external skill.
