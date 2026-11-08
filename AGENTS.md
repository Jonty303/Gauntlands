# Gauntlands — repository agent instructions

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

The `drafts/` folder contains provisional design notes, not blanket authorisation to build those features.
