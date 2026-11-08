# Character scale correction — 8 November 2026

Owner: R3 Character & Technical Artist. R2 engine-contract, R5 reproducibility and
R6 QA reviews performed sequentially by the same agent, not independent sign-off.
Scope: correct this existing adult male prototype's stature; no gameplay,
animation system, new branch, merge, or first-character artistic approval.

## Diagnosis and decision

Source `assets/Blender Models/Human-Male.blend` uses METRIC with scale_length 1.
Evaluated, helper-masked skin Z bounds are 0.0000000514 to 2.430801392:
height **2.430801340 m**. X width 1.600833893, Y depth 0.649066702.
Body, armature and eyes have zero location/rotation and unit scale, identity
world transforms. Rig is upright Z, feet face -Y. Body and eyes are children
of Human.rig. The head bone tail is 2.434778690, slightly above the skin crown;
measuring that bone would not be an anatomical height measurement.
This is a genuinely oversized saved character under the existing metre setting,
not a centimetre display issue or an MPFB sideways-coordinate artefact. The
historical cause of the original body size was not established.

Use **1.80 m** as this prototype's provisional adult male stature, preserving
all original proportions. This is a task decision, not an anatomical claim or
mandatory height for all future humans. Uniform factor **0.7404965474727526**.
Result skin height **1.800000050 m**, foot Z about 0.000000022.

## Files and reproducibility

- Original source remains byte-for-byte unchanged, SHA-256
  `19d185aaa3829b2c1b7a4b45309b7f9cc54c1804d5163d5d9907e9d5a6894ad9`.
- Open `assets/Blender Models/Human-Male-180cm.blend` for the corrected character,
  complete with eyes, existing skin/materials, rig, all nine shape keys and briefs.
- `tools/blender/normalize_human_scale.py` guards the inspected hierarchy,
  neutral pose, identity transforms, unshared data and absence of animation and
  constraints. It uniformly transforms ALL mesh data including all key blocks,
  and the armature rest data together. No mesh-only object-scale workaround.
  Object/world transforms remain identity. Camera and lights are not character data.
- The generator already derives ease, thickness and landmarks from hip separation.
  No new arbitrary clothing factor is needed; height reporting and an invalid
  hip-scale guard were added. Regenerate after changing body shape.
- `test_briefs.py` now validates either source, compares an existing garment to
  fresh generation, and frames renders relative to body size. Corrected evidence
  goes to `tools/blender/scale_previews/`, preserving the original evidence folder.
- `test_scale_export.py` produces an ignored disposable GLB and tests reimport.

PowerShell, from the Gauntlands checkout on existing `human-prototype-01`:

```powershell
$blenderExe = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
# Rebuild only after moving the existing corrected output aside; script refuses overwrite.
& $blenderExe --background --factory-startup 'assets/Blender Models/Human-Male.blend' --python-exit-code 1 --python tools/blender/normalize_human_scale.py
& $blenderExe --background --factory-startup 'assets/Blender Models/Human-Male-180cm.blend' --python-exit-code 1 --python tools/blender/test_briefs.py
& $blenderExe --background --factory-startup 'assets/Blender Models/Human-Male.blend' --python-exit-code 1 --python tools/blender/test_briefs.py
& $blenderExe --background --factory-startup 'assets/Blender Models/Human-Male-180cm.blend' --python-exit-code 1 --python tools/blender/test_scale_export.py
```

All four commands actually ran successfully with Blender **5.2.3 LTS**, build
`e13b728c6880`. MPFB was not invoked: this migrates saved geometry, not MPFB's
internal generation parameters. Do further MPFB generation in the preserved
source, then normalise a new derivative. Do not assume MPFB metadata was migrated.
The conversion refuses reruns over an existing output. No binary manual steps
are needed to obtain the delivered corrected model.

## Evidence and review

[Scale measurements](../tools/blender/scale_previews/scale_validation.json),
[clothing checks](../tools/blender/scale_previews/validation.json),
[export check](../tools/blender/scale_previews/export_validation.json),
[saved rig integrity](../tools/blender/scale_previews/integrity_validation.json).

Additional executed check: `blender --background --factory-startup --python-exit-code 1 --python tools/blender/test_scale_integrity.py` using the same full executable path. Pass: all 137 saved bone endpoints have zero scale error; saved mesh weights, material assignments, key values, parenting, parent inverses and world transforms match the original. All saved key coordinates match the scaled originals within 0.000001 m.

| Gate | Observed result |
| --- | --- |
| Source preservation | Pass: original SHA unchanged after conversion and original regression |
| Shape keys | Pass: all 9 blocks transformed, maximum coordinate error 0 |
| Mesh/eyes/rig deformation | Pass: neutral, left hip flex 45 degrees, left hip abduct 20 degrees match uniformly scaled source within 0.000000604 m |
| Saved rig rest data | Pass: 137 bones, zero endpoint scale error |
| Save/reopen | Pass: production copy height/rig link; test copy topology/UV/material checks |
| Standing and two hip poses | Pass: zero body intersection pairs, inside vertices or nonadjacent cloth self-intersections |
| Minimum measured cloth clearance | Rest 4.781 mm; flex 1.997 mm; abduct 4.809 mm |
| Garment structure | Pass: 1 component; boundary loops 44/44/64; solidified shell closed; 5,424 triangles |
| Original source regression | Pass: same original fit metrics and deterministic rerun |
| Render review | Full body, side, underside and both poses inspected; fit and proportions preserved; raised-leg cloth crease remains visible |
| GLB scale/rig round trip | Pass with explicit export settings: 1.799999695 m, armature and garment present |
| Skin/material visual fidelity | Unverified: Workbench renders do not validate textured skin; GLB reports multiple image sampler warning |
| Godot import/controllers/walk cycle | Not run; no Godot project in this checkout or godot executable on PATH |
| Extreme poses, new body shapes, MPFB editing of derivative | Unverified |
| Final human artistic acceptance | Pending user review |

[Full body](../tools/blender/scale_previews/full_body.png) ·
[Front](../tools/blender/scale_previews/front.png) ·
[Side](../tools/blender/scale_previews/side.png) ·
[Back](../tools/blender/scale_previews/back.png) ·
[Underside](../tools/blender/scale_previews/under.png) ·
[Flex](../tools/blender/scale_previews/hip_flex_45.png) ·
[Abduction](../tools/blender/scale_previews/hip_abduct_20.png).
These are actual Blender renders, not interactive desktop screenshots. Views
are reframed to body size; image height alone is not measurement evidence.

## Production unit and handoff contract

**1 Blender unit = 1 metre = 1 Godot 3D unit.** Blender uses Z up/-Y forward;
glTF handles the Y-up conversion. Do not add a manual 90-degree rotation or
100x scaling on top. Godot import scale should be 1, and instance scale 1.
Measure evaluated visible skin in neutral pose, feet to crown, excluding eyes,
helpers, bone tails, hair and garments. Record stature per character. Keep feet
at ground level and preserve the full hierarchy when migrating an existing rig.
Do not apply an isolated body transform or scale only the Basis shape key.
Unsupported transformed/animated rigs need a separate explicit migration.

Default GLB export failed the height test: **1.824266873 m**, because unapplied
helper geometry was included. The tested disposable export uses
`export_apply=True`, `export_all_influences=True`, selection only, no animation.
This bakes the current shape mix and non-armature modifiers (including mask and
cloth thickness), so exported morph count is zero; editable keys remain in the
versioned Blender file. Default four-influence truncation also emitted a warning;
the test preserves all influences. Engine weight limits, cloth post-armature
smoothing, preserve-volume behaviour and texture sampling still require R2
integration tests. Do not promote this smoke-test GLB as a production export.
A future morph-preserving export must explicitly handle MPFB helper removal and
vertex mapping rather than disabling the mask or silently losing shape keys.

R3 -> R2/R5/R6: corrected asset and tooling above, metres and axis contract above,
unchanged rig names and weights, no new animation timings. Review accepted for
scale correction and recorded Blender checks; engine integration remains unverified.
Human remains the authority for artistic sign-off and merging.

References: [Godot 3D units](https://docs.godotengine.org/en/latest/tutorials/3d/introduction_to_3d.html),
[glTF 2.0 metre/axis contract](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html).

## User acceptance — 8 November 2026

The user accepted `assets/Blender Models/Human-Male-180cm.blend` as the test
model: “We can commit this as our test model.” This is the selected character
for subsequent prototype testing on `human-prototype-01`. The original source
remains preserved. This acceptance does not certify the unverified Godot,
materials or animation checks above, authorise a merge, or expand prototype scope.
