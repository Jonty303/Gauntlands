# Gauntlands development diagrams

**Version:** 1.0 · **Recorded:** 8 November 2026 · **Status:** role-operating-model proposal; no gameplay implementation was performed.

## Diagrams

| Asset | Purpose | Source |
| --- | --- | --- |
| [DEVELOPMENT_PIPELINE.png](DEVELOPMENT_PIPELINE.png) | Design, human approval, code and asset lanes, Godot integration, QA and sign-off | [SVG](DEVELOPMENT_PIPELINE.svg) |
| [ROLE_MODEL_MAP.png](ROLE_MODEL_MAP.png) | Work type → accountable role → recommended model/tool | [SVG](ROLE_MODEL_MAP.svg) |

The SVGs are editable, version-controlled diagram sources. PNGs are static presentation exports of the same information. To regenerate a PNG from SVG on a workstation with Inkscape, use `inkscape DEVELOPMENT_PIPELINE.svg --export-filename=DEVELOPMENT_PIPELINE.png` (and analogously for the role map). Output rasterisation may differ slightly depending on installed fonts, so visually review the result before replacing a committed PNG.

## Scope and interpretation

- These drawings are aids, **not executable CI/CD configurations** or evidence that the target devcontainer and toolchain have been installed.
- Agent roles refer to [AGENT_ROLES.md](../AGENT_ROLES.md) and [AGENT_OPERATING_MODEL.md](../AGENT_OPERATING_MODEL.md).
- The code and art tracks describe future **authorised** implementation; `human-prototype-01` must not be created implicitly, and is not certified as existing.
- `main` accepts expressly authorised documentation and configuration records only for this task; no prototype commits, new branches or merges were performed.
- Model names are recommendations as of **8 November 2026** and subject to changes in the user's model picker and plan; source: [OpenAI Work and Codex](https://help.openai.com/en/articles/20001275-chatgpt-work-and-codex).
- Image generation is for visual concepts only; it does not produce usable Blender meshes or a rig. Final assets, imports, playtests and visual checks require actual application execution.
