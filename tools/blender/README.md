# Fitted boxer briefs v2 — human-prototype-01

This replaces the rejected face-extraction generator with a new, connected garment
mesh. Tested in **Blender 5.2.3 LTS** (e13b728c6880) against the committed
`assets/Blender Models/Human-Male.blend`. Installed MPFB manifest: **2.0.18**.
MPFB does not need to be enabled to run this generator: the saved shape keys,
mask and rig supply the inputs. Human artistic approval remains pending.

## Run in Blender

1. Update your clean checkout of **Jonty303/Gauntlands**, existing branch
   `human-prototype-01`. Preserve any local changes before pulling.
2. Open the original `assets/Blender Models/Human-Male.blend`. Choose **Save As**
   and use a different filename, for example `Human-Male-Briefs-test.blend`.
3. Use Object Mode and the neutral rig pose. In Scripting, open
   `tools/blender/generate_briefs.py`, then press **Alt+P** over the text editor.
4. Inspect `Gauntlands_Boxer_Briefs` in front/back/side and underneath. The script
   finds the MPFB body by its body group and shape keys; selection is irrelevant.
5. Save only your test copy. The generator itself never saves any file.

If v1 briefs are already in the scene, hide or remove that rejected garment first.
Rerunning v2 preserves existing objects and produces `.001`, `.002`, etc.; these
occupy the same space, so hide the earlier version when comparing. It does not
silently replace hand edits. Geometry is deterministic on the same source.

## Geometry and rig contract

- Source skin: current shape-key mix evaluated with the helper mask, without
  armature deformation. A temporary object is removed after sampling; original
  mesh, modifiers, shape keys and rig remain unchanged.
- Coordinate frame: hip separation gives left/right; pelvis-to-head gives up;
  foot direction identifies front. Object transforms are carried into the rig
  frame. This is an MPFB default-rig-specific tool, not a universal clothes fitter.
- Waist follows the `spine04` head (lower abdomen/hip line); hem follows the upper
  thigh landmark with a short extension. No full-body-height percentage is used.
- A 64-point torso ring transitions into two 44-point leg rings, sharing a sewn
  front-to-back crotch bridge. This is one connected all-quad surface with exactly
  three boundary loops: waist and two legs. The crotch has no opening.
- Ray samples exit the torso or the corresponding thigh, avoiding hands and the
  opposite leg. Fabric ease is 0.016 rig units at the measured hip width, with
  extra crotch clearance; Solidify adds 0.0015 units outward thickness.
- Deform weights are interpolated on evaluated skin triangles, normalised, then
  smoothed below the waistband to avoid sudden left/right-thigh changes.
  A four-pass Smooth modifier after the armature softens compressed cloth folds
  before thickness is added.
  The garment uses the original `Human.rig` and its preserve-volume setting.
- Packed UV islands, two opaque rough materials, smooth normals. UVs are usable
  for painting but are not a tailored sewing-pattern atlas. No image textures.
- Task budgets: <=5,000 base triangles; <=6,000 after thickness; two materials.
  Actual: 1,355 vertices / 1,280 quads / 2,560 base triangles; 5,424 solidified
  triangles; two materials, one UV layer. These are task limits, not project-wide.

## Reproduce validation

From the repository root in PowerShell:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' `
  --background --factory-startup 'assets/Blender Models/Human-Male.blend' `
  --python-exit-code 1 --python tools/blender/test_briefs.py
```

The test writes six actual Blender Workbench renders and `validation.json` under
[previews](previews/), plus an ignored test `.blend`. It saves and reopens that
separate copy and checks that the source file SHA-256 is unchanged. Run against
the pristine committed source; it deliberately asserts the inspected contract.
The test script changes the disposable scene's camera/render settings and poses;
the generator does not. Grey skin in previews is the source viewport material.

## Acceptance and evidence

| Criterion | Result |
| --- | --- |
| Waist at hips, short thigh coverage, closed crotch | Pass: front, side, back, underside renders reviewed |
| One connected surface / three intended openings | Pass: boundary lengths 64, 44, 44; no invalid edges or degenerate faces |
| Thickness closes the shell | Pass: zero boundary edges after Solidify |
| Skin fit in standing, 45-degree left hip flexion, 20-degree left abduction | Pass: zero skin and non-adjacent self-intersection pairs in all three cases |
| Normalised deform weights, rig link, UVs and two materials | Pass: automated checks |
| Non-destructive rerun | Pass: different object name, identical generated coordinates, source data unchanged |
| Save/reopen test copy | Pass: topology, rig, UVs and materials checked after reopen |
| Source file preserved | Pass: SHA-256 unchanged; source asset not included in the change |
| Full walk cycle, both legs together, deep squat, extreme poses | Not tested |
| GLB export / Godot import / controller testing | Not tested; outside this generator repair |
| Final character artistic approval | Pending user review |

[Front](previews/front.png) · [Side](previews/side.png) · [Back](previews/back.png) ·
[Underside](previews/under.png) · [Raised leg](previews/hip_flex_45.png) ·
[Sideways leg](previews/hip_abduct_20.png) · [Measurements](previews/validation.json)

The body is unusually tall (2.4308 scene units). Do not interpret its units as a
new real-world character-height decision. No rescaling of the human is performed.
After editing body shape keys, regenerate the garment in neutral pose; it does
not inherit those shape keys automatically. Unsupported rigs or non-neutral poses
are rejected. Animation clearance beyond the recorded poses is unverified.

See [failure analysis and handoff](../../development/BRIEFS_V2_REVIEW.md).
