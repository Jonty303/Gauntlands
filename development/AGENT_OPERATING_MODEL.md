# Gauntlands — agent operating model and hand-offs

**Version:** 1.0 · **Recorded:** 8 November 2026 · **Status:** proposed, ready for project-owner review  
**Source of role definitions:** [AGENT_ROLES.md](AGENT_ROLES.md)  
**Authority:** [PROJECT_CUSTOM_INSTRUCTIONS.md](PROJECT_CUSTOM_INSTRUCTIONS.md) and approved specifications.

## Working principle

The roles are **named hats and deliverable contracts**, not provisioned autonomous processes. ChatGPT helps design and review; Codex or a connected implementation environment changes files; Blender and Godot actually execute and validate their respective work. Choosing Astra or another model never grants filesystem, application or repository access.

## Standard request-to-sign-off sequence

| Gate | Responsible | Input | Required output / evidence |
| --- | --- | --- | --- |
| 0. Intake | L0 | Request and known references | Primary role, bounded task, constraints, repo and branch identification |
| 1. Design | R1 with R3/R4/R2 as needed | Approved context, drafts labelled provisional | Requirements and acceptance criteria, dependencies, decisions explicitly pending |
| 2. Human scope approval | Human | Gate 1 brief | Approval for substantial implementation and any branch-sensitive work |
| 3. Implementation | R2, R3, R4 or R5 (one owner) | Approved task and compatible toolchain | Reproducible changes and evidence; use smallest feasible slice |
| 4. Integration | R2 + R3/R4 | Exports, code, manifest | Godot import and execution, revised assets only when needed |
| 5. Verification | R6 | Specification and artifacts | Automated logs + human visual/manual evidence, pass/fail/not-run, open defects |
| 6. Review and acceptance | L0, then human | Gate 5 findings | Explicit decision: accept, revise or defer; no implicit merge |
| 7. Record | L0 + R5 | Accepted work | Docs, version/dependency updates, commit references and follow-up limitations |

A failed gate loops to the **owning role**; do not blur a design-change request into a bug fix. If requirements materially change, return to Gate 1.

## Where work runs

| Environment | Routine roles | Capabilities / limits |
| --- | --- | --- |
| **iPad** | L0, R1, R4, review with R6 | ChatGPT discussions, reference images, specification writing, GitHub and browser Codespaces review. It is not a local Blender/Godot execution engine. |
| **Windows desktop** | R3, R4, R2, R6 | Interactive Blender/MPFB, Godot editor and playtesting, controller tests, source inspection; Codex can assist with locally authorised scripts. |
| **Codespaces** | R2, R5, R6 | Code, documentation, scripts, headless Godot/Blender checks **after** dependencies exist. A Codespace is not the same as Codex Cloud. No guaranteed GPU/interactive Blender. |
| **GitHub** | All roles | Versioned source of truth; reviewable commits and decisions. A chat transcript alone is not a source artifact. |

## Model selection and escalation

- **GPT-6 Medium (Chat):** Drafting, brainstorming, routine planning and dialogue; switch to High if architectural trade-offs or complex balance matter.
- **GPT-6 High (Chat):** Systems architecture, requirements, cross-role design reviews, complex root-cause reasoning, acceptance design.
- **Image generation:** Static concept/reference images when expressly requested. It does not create editable meshes, animation rigs, GDScript or validated gameplay.
- **Codex (coding model available in its picker):** Repository edits, Python/Blender automation scripts, GDScript, devcontainers and executable tests. Start with an efficient available coding model (for example Sol if offered).
- **GPT-6 Astra in Work/Codex, if available:** Escalation for novel rigging automation, difficult Godot defects, complex design/code interactions and multi-step technical investigations. Do not consume scarce access for routine markdown or simple edits.
- **Blender / Godot:** Execution and manual quality control still required. Models cannot certify that the software was run without tool evidence.

This model mapping is **a snapshot, not a pinned build dependency**. As of 8 November 2026, OpenAI documents limited Astra use in Work/Codex on Plus; in ordinary Chat, GPT-6 High is available on eligible paid plans, while Astra-backed Chat Pro has separate eligibility. See [ChatGPT Work & Codex](https://help.openai.com/en/articles/20001275-chatgpt-work-and-codex) and [GPT-6](https://help.openai.com/en/articles/20001354-gpt-6-and-other-models-in-chatgpt). Check the actual picker and allowance before scheduling work.

## Focused human prototype — first end-to-end acceptance example

**Current intended task:** underwear-only believable human on a single flat Godot test plane, walking in eight directions. The goal is a reusable Blender generation, rig, skinning and animation pipeline, **not** the full class roster, weapon system or level design.

1. **L0 + R1:** Define body/animation constraints and acceptance criteria; distinguish approved visual targets from exploration.
2. **R3:** Set up MPFB-human generation, skin material, rig and walk cycles in desktop Blender; retain editable source and export manifest. Verify installed versions before automating.
3. **R5:** Provide reproducible scripts and checks; Codespaces setup only after explicitly authorised, with no assumption MPFB will work headlessly.
4. **R2:** Import GLB into Godot 4.5.2, connect one controllable character and a flat plane, wire eight directional movement.
5. **R6:** Confirm no missing materials, clean Godot import, plausible foot contact, joints/skin weights, direction-dependent animation and repeatable run/test evidence.
6. **L0 + human:** Review visuals and behaviour; record explicit approval or defects. Only then consider the next development stage.

**Branch gate:** `human-prototype-01` must be created from `main` when explicitly authorised. Until it exists and is confirmed, **do not** commit prototype code to `main` or open alternate branches.

## Definition of ready

- Repository and target branch verified; current workspace clean or existing changes preserved.
- References and decision status named; cross-project contamination excluded.
- Primary owner and necessary reviewers named.
- In/out of scope, dependencies, acceptance criteria and artifacts/path specified.
- Testing method identified, including manual evidence when needed.

## Definition of done

- Only authorised files changed; diff understood; reusable interfaces documented.
- All applicable checks run; failing or not-run checks disclosed honestly.
- Asset provenance, licence, versions and tooling recorded where relevant.
- Visual and interactive claims supported by desktop screenshots/video or witnessed review.
- Acceptance criteria traced to evidence; unresolved risks named.
- Human approval captured before first-character sign-off or merges.
- Documentation in `development/` updated when environment or pipeline changes.

## Documentation map

- [AGENT_ROLES.md](AGENT_ROLES.md) — ownership and role charters.
- [PROJECT_CUSTOM_INSTRUCTIONS.md](PROJECT_CUSTOM_INSTRUCTIONS.md) — project-wide behaviour and safety.
- [TARGET_DEVELOPMENT_ENVIRONMENT.md](TARGET_DEVELOPMENT_ENVIRONMENT.md) — target environment and recreation checklist.
- [diagrams/README.md](diagrams/README.md) — pipeline and role/model visuals plus source/recreation notes.
- [Root AGENTS.md](../AGENTS.md) — concise Codex/repository entrypoint.

## Change control

These role allocations are an initial proposal. Changes to responsibilities, tools, models, acceptance gates or environment assumptions require a reviewed revision date, reason and affected docs. Do not promote drafts under `drafts/` to approved specs accidentally.
