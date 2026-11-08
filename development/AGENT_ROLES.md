# Gauntlands — agent roles and ownership

**Version:** 1.0 · **Recorded:** 8 November 2026 · **Status:** proposed operating model for review  
**Repository:** [Jonty303/Gauntlands](https://github.com/Jonty303/Gauntlands) · **Branch for this record:** `main`

## Purpose and boundaries

These are **specialist responsibilities and task prompts**, not a claim that seven independently running agents, Blender integrations, or Codex automations have been installed. A person or a single assistant session may perform multiple roles, but the deliverable must identify its *primary owner*, reviewers and evidence. The human project owner makes scope, artistic-direction, prototype sign-off and merge decisions.

Read [Project Custom Instructions](PROJECT_CUSTOM_INSTRUCTIONS.md), [Target Development Environment](TARGET_DEVELOPMENT_ENVIRONMENT.md) and [Agent Operating Model](AGENT_OPERATING_MODEL.md). Approved specifications take precedence over drafts. The other private Gold Box-style RPG is out of scope: no shared repository access, imports, copied assets or assumed design contracts.

## Role register

| ID | Role | Owns | Primary hand-off | Typical model and execution |
| --- | --- | --- | --- | --- |
| **L0** | **Production Lead / Technical Integrator** | Scope, priorities, architecture decisions, acceptance gates, cross-discipline decisions and conflict resolution | Task brief + decision log; integrates evidence for human sign-off | GPT-6 High in Chat; Codex for permitted repository tasks |
| **R1** | **Game Design & Systems Designer** | Rules, controls, progression, combat contracts, encounter requirements and measurable acceptance criteria | Approved mechanic/interaction specification to R2/R3/R6 | GPT-6 High for systems; Medium for drafting/iteration |
| **R2** | **Godot Gameplay Engineer** | GDScript, scenes, controllers, gameplay state, input, AI, import integration and in-engine behaviour | Working Godot change + tests/import evidence to R6 | Codex using available coding model; Astra for difficult debugging |
| **R3** | **Character & Technical Artist** | Blender models, topology, MPFB workflow, skin/material setup, reusable rigs, skinning, animation, GLB export | Versioned .blend/exports + skeleton/material/animation manifest to R2/R6 | GPT-6 High for specifications, Codex for Blender scripts; Blender executes |
| **R4** | **Art Director & Rendering Artist** | Style references, silhouette/material standards, environment kit, lighting, shaders, VFX and visual consistency | Art brief, references, materials/shader settings, screenshots to R3/R2/R6 | GPT-6 Medium/High; image generation for concepts; Blender/Godot for final assets |
| **R5** | **Pipeline & DevOps Engineer** | Repository conventions, Codespaces, dependency pins, validation scripts, export automation, Git hygiene, reproducibility | Working automation/configuration + rebuild evidence to all roles | Codex for implementation; Astra for complex pipeline faults |
| **R6** | **QA & Integration Engineer** | Traceability, headless checks, interactive test cases, regression, import checks, performance evidence, defects | Test report, reproducible defects and risk assessment to L0 | Codex for automated tests; GPT-6 High for diagnosis/review; human visual tests |

**The models are recommendations, not hard requirements.** Model menus, availability and usage allowances change. In current OpenAI guidance, GPT-6 High is a Chat reasoning option; Codex/Work exposes its own available coding models including Astra (limited use on Plus); the assistant still requires the correct workspace and tools to execute software. See [OpenAI: Work and Codex](https://help.openai.com/en/articles/20001275-chatgpt-work-and-codex) and [Astra usage](https://help.openai.com/en/articles/20001516-managing-usage-with-gpt-6-astra-in-work-and-codex).

## Individual role charters

### L0 — Production Lead / Technical Integrator
- **Owns:** Translate a request into one bounded work package; nominate a primary owner and consulted reviewers; protect scope, conventions, reuse and schedule; record trade-offs and decisions.
- **Required inputs:** Human objective, latest approved specification/visual references, repository/branch status, dependencies and constraints.
- **Produces:** Brief with in/out-of-scope, acceptance criteria, affected files, owner/reviewer, test expectations, decision status and sign-off request.
- **Does not:** Treat a generated mock-up as approved production art; grant itself permission to merge or add branches; override human decisions.
- **Gate:** R1/R3/R4 agree requirements and feasibility before substantial implementation; R6 evidence before requesting human approval.

### R1 — Game Design & Systems Designer
- **Owns:** Character controls, attack/range/defence behaviour, class differentiation, powers, level and encounter design; define measurable gameplay outcomes and edge cases.
- **Required inputs:** Human gameplay intent, existing approved mechanics, playtest observations and constraints.
- **Produces:** Versioned rule specification, state/flow examples, acceptance scenarios, required telemetry and list of provisional decisions.
- **Does not:** Commit gameplay implementations or silently promote roadmap ideas to Stage 01.
- **Gate:** L0 reviews for scope; R2 confirms technical testability; R6 converts acceptance into test cases.

### R2 — Godot Gameplay Engineer
- **Owns:** Godot 4.5.2 baseline (unless changed), GDScript, scene structure, input maps, navigation, camera, animation state integration, import and reusable gameplay components.
- **Required inputs:** Accepted design contract, R3 exports/rig contract, R4 look requirements and R5 toolchain.
- **Produces:** Minimal diff, typed contracts where useful, import settings, automated checks, reproducible test scene and manual-test notes.
- **Does not:** Redesign accepted game rules, overwrite artist source files, add speculative weapon systems or treat headless runs as visual validation.
- **Gate:** Parse/import tests must pass; R6 verifies interaction and regression; L0 resolves architecture conflicts.

### R3 — Character & Technical Artist
- **Owns:** Human anatomy/proportions and topology, procedural Blender/MPFB setup, material slots, rig hierarchy and naming, UV/skin weights, animation loops, retargeting, GLB export quality.
- **Required inputs:** Approved body reference and visual specifications, R2 skeleton/animation contract, target engine, technical constraints.
- **Produces:** Editable Blender source, export(s), scale/axis/rig manifest, versions, reproduction script, turntable/screenshot evidence and known limitations.
- **Does not:** Assume MPFB can run headlessly in Codespaces before proven; convert an underwear-only prototype into a dressed character; invent additional branches.
- **Gate:** Human inspects pose, joints, walk cycle, surface quality; R2 imports in Godot and R6 checks eight-direction motion.

### R4 — Art Director & Rendering Artist
- **Owns:** Cohesive dark-fantasy art direction, readable character silhouettes, concept/reference boards, surfaces, shader treatments, world kit materials, scene lighting and composition.
- **Required inputs:** Approved references, engine performance limits, scene purpose and R3 model constraints.
- **Produces:** Visual brief with labelled approved/provisional elements, images/mock-ups, material/shader targets, comparison frames and art QA checklist.
- **Does not:** Treat image-generated designs as automatically riggable or optimised 3D assets; add costume detail or cloaks without scope approval.
- **Gate:** Human explicitly accepts the visual target; R3/R2 check technical feasibility; R6 checks in-engine consistency.

### R5 — Pipeline & DevOps Engineer
- **Owns:** Devcontainer, Windows/toolchain version matrix, Git/branch hygiene, GLB/asset conventions, reproducible builds, lint/import scripts, safe CI and diagnostics.
- **Required inputs:** Authorised repository/branch, approved build dependencies, R2/R3 validation needs and current environment evidence.
- **Produces:** Pinned configuration, instructions, minimal scripts, rebuild logs, tool-version records, failure handling and recovery procedure.
- **Does not:** Store credentials in Git, install unapproved third-party automation, alter GitHub branch protection without permission or automatically push to `main`.
- **Gate:** Fresh recreation test with independent environment, then R6 validates reproducibility.

### R6 — QA & Integration Engineer
- **Owns:** Requirements-to-test traceability, risk-based regression, Godot headless import/parser tests, asset inspection, interactive controller and visual review, defect triage and performance baselines.
- **Required inputs:** Scope/acceptance spec, artifacts, reproduction instructions and expected platform.
- **Produces:** Pass/fail/not-run matrix, screenshots/logs and precise reproduction steps, severity and residual risks; clear distinction between automated and manual results.
- **Does not:** Mark visually inspected, performance-tested or signed-off unless verified; change acceptance criteria to hide a failure.
- **Gate:** L0 reviews evidence and seeks explicit human sign-off where required.

## Cross-role ownership rules

1. **One primary owner per work package**; other roles are named reviewers. Do not create seven parallel agents for every small change.
2. **Design first, implement second.** Work enters implementation only with scope, relevant reference, acceptance criteria, dependency plan and location/branch check.
3. **Small iteration, demonstrable result.** A single human on a flat Godot plane with eight-direction walking is the current character prototype boundary; do not pre-build the wider game.
4. **Reusable by contract, not assertion.** Shared rigs/animations/controllers require an in-engine compatibility test, especially for later dwarf/halfling bodies.
5. **Evidence before claims.** Record commands actually run, versions, results, screenshots and manual observations separately. Not-run is not pass.
6. **Human is the approval authority.** L0 cannot merge to `main`, approve the first underwear-only human or create additional branches on the human's behalf.

## Git restrictions (binding)

- `main` holds approved documentation and explicitly authorised repository configuration records. This role documentation is documentation-only and is authorised for `main`; prototype code and artwork must not be introduced by this change.
- The first human work belongs to **one** branch: `human-prototype-01`, originating at `main`. This branch was **not present at the last documented inspection**; do not claim it exists or create it implicitly.
- **No other branches** before the human explicitly signs off the first underwear-only human. No merge into `main` without express approval. Never use a new worktree that silently creates a branch, and never force-push.
- Confirm repository, checkout, branch and uncommitted work before any operation. Keep `Jonty303/Project-Gauntlands-Archive` and the private Gold Box RPG separate.

## Agent role invocation template

```text
Role: [L0/R1/R2/R3/R4/R5/R6]  Primary owner: [...]
Repository: Jonty303/Gauntlands  Branch: [verified existing branch]
Goal / approved reference: [...]
In scope: [...]  Out of scope: [...]
Inputs / required dependencies: [...]
Deliverables (paths): [...]
Acceptance criteria (observable): [...]
Tests and evidence: [...]
Reviewers and human approval required: [...]
```

See the [operating model](AGENT_OPERATING_MODEL.md) for hand-offs, definition of done and the two diagrams in [diagrams/](diagrams/).
