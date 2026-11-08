# Gauntlands — target development environment

Last reviewed: 8 November 2026  
Status: Recreation reference and proposed setup baseline; installation is not certified.

## Repository and authority

Use [Jonty303/Gauntlands](https://github.com/Jonty303/Gauntlands).
The local checkout inspected for this reference is `S:\OneDrive\__Github\Gauntlands`.
The similarly named `Project-Gauntlands` checkout points to
`Jonty303/Project-Gauntlands-Archive` and is not the new project.

The existing local `development/` folder was empty. Git does not track empty
directories; this document makes that folder visible on GitHub.
The new repository has no configured agent roles. Do not copy the archive's
role system, iteration contracts or 2D/3D architecture decisions into it.
See the existing [design drafts](../drafts/README.md) for their explicitly
provisional scope. Environment setup does not authorise gameplay or asset production.

The referenced “Choose ChatGPT Models” conversation established the requested
three-environment topic, but its assistant replies were available only as reference
placeholders when this file was written. Accordingly, unspecified versions and
settings below are recommendations or open decisions, not recovered agreements.

### Branch restrictions

- Use existing `human-prototype-01` for its intended prototype work if it exists.
- At inspection, GitHub and the local new-project checkout contained only `main`;
  `human-prototype-01` was absent. This reference is added to existing `main`.
- Do not create `human-prototype-01`, another branch, or a branch-producing worktree
  without explicit approval. Do not start prototype implementation on `main`
  merely because the requested prototype branch is absent.
- Do not merge or copy archived experiments automatically. Do not force-push.
- Before any edit, verify repository, branch and working-tree status. Preserve
  uncommitted work and pull only when it is safe.

## Target division of work

| Environment | Intended responsibilities | Execution location |
| --- | --- | --- |
| iPad | Planning, reference review, ChatGPT discussions, GitHub review, browser access to Codespaces | Browser/cloud; no local Blender toolchain assumed |
| Windows desktop | Blender/MPFB modelling and animation, Godot editor and interactive tests, local Codex work | Windows checkout and installed applications |
| GitHub Codespaces | Portable editing, scripts, documentation, automated checks and supported headless builds | Linux devcontainer attached to the correct repository |

GitHub commits are the handoff between desktop and Codespaces. A ChatGPT
conversation is not a synchronised filesystem. A Codespace is also separate
from a Codex cloud environment; configuring one does not configure the other.
Use one active writer per branch/file set and commit/push before handing work over.

## Prerequisites and version record

- GitHub account with repository write access and account recovery/2FA configured.
  Confirm Codespaces entitlement, billing limits and organisation restrictions
  before creating a Codespace.
- ChatGPT account with the required Codex features available. Check the actual
  account/workspace rather than assuming a particular subscription or model.
- Windows machine capable of running the selected Blender and Godot builds,
  sufficient disk space for source assets/import caches, and a controller for
  interactive gameplay testing.
- iPad with an up-to-date browser and reliable internet; keyboard and pointing
  device are useful for browser editing.
- Git for Windows and an editor such as VS Code on desktop. GitHub CLI is optional.
  Docker Desktop/WSL is optional for local devcontainer reproduction, not required
  simply to use hosted Codespaces.
- **Godot baseline: 4.5.2 stable**, unless explicitly changed for this project.
  Use the same version on desktop and in automated checks. Standard versus .NET
  must be chosen before introducing C#; do not add .NET requirements speculatively.
- **Blender/MPFB versions: not yet pinned.** Select a mutually supported stable
  pair and record exact patch/release versions after the smoke test. MPFB 2's
  published guide requires Blender 4.2 or later; that minimum alone is not proof
  that every later Blender build is compatible. Standalone MakeHuman is not
  required for MPFB 2. See [MPFB getting started](https://www.makehumancommunity.org/mpfb/docs/getting_started.html).

Before calling the environment reproducible, record the Blender build, MPFB
release, asset-pack versions and licences, Godot build, Git and Codex versions,
Node version if used, devcontainer image digest, and installer download URLs and
checksums. Do not substitute “latest” for these records.

## Setup sequence

### 1. Establish GitHub and the working copy

1. Confirm the remote is `https://github.com/Jonty303/Gauntlands.git`.
2. On a new computer clone that repository; on an existing computer inspect the
   checkout before changing anything.
3. Configure Git author name/email and HTTPS credential-manager or SSH
   authentication. Keep credentials out of repository files.
4. Fetch and inspect branches without creating one:

   ```sh
   git remote -v
   git status --short --branch
   git fetch origin
   git branch --all
   git ls-remote --heads origin human-prototype-01
   ```

5. If the prototype branch exists locally, switch to it only with a safe working
   tree. If it exists only remotely, check it out as a tracking branch without
   creating a new remote branch. If absent, stop prototype setup at the
   documentation/tool-installation stage and request approval before creation.
6. Review repository rules and any future instructions before implementation.
   Branch-protection settings were not audited or changed for this reference.

Agree an asset-storage policy before large binary submissions. If Git LFS is
adopted, install it in both working environments and commit the agreed
`.gitattributes` before adding those binaries; do not rewrite existing history.
Use Git for handoff rather than relying on OneDrive to synchronise an active
working copy. Never edit the same checkout simultaneously from two machines.

### 2. Configure Windows desktop

1. Install Git and the chosen editor; open the new Gauntlands checkout.
2. Install Godot 4.5.2 from its [official archive](https://godotengine.org/download/archive/4.5.2-stable/).
   Make a `godot` command available, or document the full executable path.
   Install matching export templates only when exports are needed.
3. Install the selected Blender build from the official distribution and retain
   its installer/version information. Make `blender` available in the terminal
   if scripts will invoke it.
4. Install MPFB through the installation method documented for the chosen release;
   enable it in Blender and save preferences. Install required MakeHuman system
   assets and any approved additional packs. Record asset locations and licences.
5. Create a disposable MPFB human, save the `.blend`, restart Blender and reopen
   it. Check materials, rig if used, and missing-file warnings. This is a tool
   smoke test, not approval of a production character.
6. For an approved asset pipeline, retain editable source and use an agreed
   export such as glTF/GLB for Godot. Validate scale, facing, skeleton and materials
   in a scratch scene before production. Prefer explicit exports for automation
   so imports do not silently depend on an unconfigured Blender executable.
7. Do not invent polygon budgets, rig conventions or animation contracts in this
   environment document; define them with the first authorised asset task.

### 3. Configure ChatGPT/Codex

Follow the [official quickstart](https://learn.chatgpt.com/docs/quickstart) and
[authentication guide](https://learn.chatgpt.com/docs/auth) for the installed client.

- On desktop, sign in and select the actual Gauntlands working directory.
  Verify the displayed repository/branch before requesting edits.
- For repository-aware cloud work, connect GitHub and grant access to
  `Jonty303/Gauntlands`. Verify access with a read-only file request.
  A GitHub connection does not grant access to desktop Blender or its filesystem.
- For terminal work, install the official Codex CLI using its supported
  installation method and record its version. Use ChatGPT sign-in when available;
  API-key authentication is a separate option with its own billing.
- For remote/headless sign-in, follow the documented supported remote login
  flow. Do not copy tokens into Git or bake authentication into a container image.
- Keep normal permission controls. Start with a read-only orientation request,
  then ask for one bounded change and review the diff and validation.
- Include repository, branch restriction, deliverable, relevant source files and
  acceptance criteria in tasks. There are no project-specific agent roles yet.
- Model choice is not a Blender installation requirement. Use a suitable available
  coding model for routine edits; reserve deeper reasoning for difficult design,
  debugging or review. No Astra-specific requirement is established here.
  Tool access and executable validation remain necessary regardless of model.

No Blender MCP bridge or other remote-control integration is assumed installed.
If one is later selected, document its exact version, permissions, connection
method and a harmless connection test before relying on it.

### 4. Configure Codespaces and the devcontainer

Create a Codespace from the verified repository and an authorised existing branch.
Check the branch again inside its terminal. Choose a machine size based on actual
workload and account limits; no hardware budget has been agreed yet.

**Current state:** No `.devcontainer/` configuration or Godot project was present
in the inspected GitHub tree. The following is a target contract, not an installed
or tested container.

When implementation is authorised, add:

| Proposed file | Required responsibility |
| --- | --- |
| `.devcontainer/devcontainer.json` | Select the pinned image/Dockerfile, working user and shared editor settings |
| `.devcontainer/Dockerfile` | Install pinned tools and Linux libraries; verify downloaded binaries |
| `.devcontainer/setup.sh` | Idempotent non-secret workspace setup, if needed |
| `.devcontainer/validate.sh` | Report versions and run checks that actually exist |

Include Git, certificates, download/archive utilities, Python for project scripts,
and the exact Linux Godot build. Add Node and a pinned Codex CLI only if terminal
Codex is part of the chosen setup. Include Blender/MPFB only if authorised
headless asset jobs require them; desktop interactive modelling remains the
baseline. Do not assume a Codespace provides GPU rendering or a desktop GUI.

Keep credentials in supported account/secret storage, not Dockerfile layers or
checked-in files. Make setup repeatable and fail clearly on version/download
errors. Rebuild the container after configuration changes, then test a fresh
Codespace to expose dependencies that existed only in a previous session.
Stop unused Codespaces and manage retention/billing settings.

GitHub documents [devcontainer configuration and rebuild behaviour](https://docs.github.com/en/codespaces/setting-up-your-project-for-codespaces/adding-a-dev-container-configuration/introduction-to-dev-containers).
Until a project configuration exists, Codespaces uses its default environment;
that is not a verified Gauntlands toolchain.

### 5. Configure iPad access

1. Sign in to ChatGPT and GitHub with the intended accounts.
2. Open the repository in the browser and verify the branch and documentation.
3. Open the authorised Codespace in the browser editor; confirm terminal access,
   repository remote and branch. Tools run in Linux, not on the iPad.
4. Use ChatGPT for planning and reviewing captures; send concrete repository
   context with implementation requests.
5. If interactive Blender/Godot access is needed from iPad, arrange a separately
   secured remote-desktop connection to Windows and test input/display usability.
   This is optional and no remote-desktop product is prescribed here.
6. Push completed work before switching environments. Pull it safely on desktop
   and perform interactive validation there.

## Validation and recreation checklist

Run version checks in each applicable execution environment:

```sh
git --version
git remote -v
git status --short --branch
godot --version
blender --version
codex --version
```

Run only installed/applicable tools; record missing tools as missing, not passes.
On Windows, use full executable paths if they are not on PATH.

Once an actual Godot project exists, run from its directory:

```sh
godot --headless --editor --path . --quit
```

Require a successful exit and no parser/resource-load errors. Then run the
project's narrow relevant tests once they exist. Test rendering, controller
input, animation and gameplay interactively on desktop; a headless pass does
not establish those results.

| Gate | Required evidence | Status when this document was created |
| --- | --- | --- |
| Correct repository and branch | Remote, local branch list, GitHub branch list | Verified: new Gauntlands; main only |
| Development destination | Local folder inspection | Verified: existing empty folder |
| Roles/configuration | Repository tree and user clarification | No configured roles or devcontainer |
| Desktop toolchain | Versions plus Blender/MPFB save/reopen | Not run |
| Codespaces rebuild | Fresh creation/rebuild logs and tool checks | Not run |
| iPad access | Browser editor/terminal and repository check | Not run |
| Godot project validation | Import log, exit status, relevant tests | Not applicable yet: no project in inspected tree |
| Cross-environment handoff | Same commit and expected files on both machines | Not run |

This change adds documentation only; it does not install software, create a
Codespace, configure accounts, add roles, create branches or certify gameplay.
Recreation is complete only after the pending checks pass and exact tool versions
are recorded. Keep remaining compatibility decisions explicit rather than treating
this proposed baseline as a previously tested environment.
