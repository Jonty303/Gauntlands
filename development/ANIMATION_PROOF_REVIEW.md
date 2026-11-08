# Animated character export proof — 8 November 2026

## Approved task and result

User authorised the next bounded step toward Prototype 01: diagnostic animation
in Blender, imported into a minimal Godot scene. R3 leads; R2 engine integration,
R5 pipeline and R6 QA performed sequentially by one agent. This is not an
independent multi-agent sign-off. Existing branch `human-prototype-01` only.

**Result:** the accepted 1.80 m human and fitted briefs now animate in Godot
4.5.2, with embedded skin/eye textures. The eight-second diagnostic survives
export and import with the full 137-bone hierarchy. The first walking milestone
is still ahead: idle, walk, ground contact, transitions and gamepad movement.

## Deliverables and interface

- [Editable animated source](../assets/Blender%20Models/Human-Male-Animation-Proof.blend):
  separate derivative; all nine editable shape keys remain. Used skin and eye
  images are packed. Original and accepted 180cm sources were not modified.
- [Godot project](../prototype/project.godot) and [viewer instructions](../prototype/README.md).
- [GLB](../prototype/assets/human_diagnostic.glb): neutral current shape baked;
  helper mask, eye subdivision and clothing modifiers baked; one `Diagnostic`
  action. No morph targets. Standard linear skinning; maximum eight influences
  per vertex, highest weights retained and normalised by the exporter.
- [Build script](../tools/blender/build_animation_proof.py),
  [Blender export test](../tools/blender/test_animation_export.py),
  [Godot import test](../prototype/tests/test_import.gd).
- [Build manifest](../tools/blender/animation_previews/build.json),
  [241-frame exported-clothing report](../tools/blender/animation_previews/export_animation_validation.json),
  [Godot geometry comparison](../tools/blender/animation_previews/godot_validation.json).

Metres throughout, object/import scale 1. Blender Z-up/-Y-forward becomes Godot
Y-up/+Z-facing through glTF basis conversion. No manual compensation rotation.
This is mesh facing, not a future movement-controller direction convention.
Blender frames 1–241, 30 fps; export explicitly slides start to zero for exactly
8 seconds. Neutral at 0, 2, 4, 6 and 8 seconds; left leg peak at 1, right leg at
3, arm swing at 5, head turns at 6.5 and 7. Ranges: hips 30 degrees, knees 45,
arms 25, head +/-25. Root remains stationary. No IK or root-motion contract added.

## Validation actually performed

| Gate | Result |
| --- | --- |
| Accepted source preserved | Pass: SHA-256 remains `a4bd547d659e928b132f530f166d96fd20e9001fedb09dcc424e7c65c0fc1d75` |
| Saved animated .blend reopened | Pass: Diagnostic action, 9 shape keys, both used images packed |
| Exported clothing | Pass at all 241 integer frames: zero body intersections, inside vertices or nonadjacent self-intersections; smallest sampled clearance 4.673 mm |
| glTF seam handling | Self-intersection check treats shared geometric corners at UV/material splits as adjacent (coordinates rounded to 0.01 mm) |
| Godot editor import/parser | Pass: Godot 4.5.2 stable `6ce3de25a`, no parser/resource errors |
| Engine skeleton/animation | Pass: 137 bones; one 8-second diagnostic; body, eyes and briefs skinned; both embedded albedo textures present |
| Fresh-copy import | Pass: copied project without .godot cache to a new temporary directory; editor import and geometry test passed with the same maximum error |
| Engine stature | Pass: neutral evaluated skin height 1.799999698 m |
| Engine vs Blender GLB evaluation | Pass: 10 diagnostic times, all 3 meshes, all axis-aligned bounds within 0.1 mm tolerance; observed maximum 0.050307 mm |
| Actual rendering | Pass: seven Godot GPU captures on NVIDIA RTX 2070, OpenGL Compatibility; captures reviewed for body/eye attachment, cloth fit and basic pose integrity |
| Human interactive review | Not performed by user yet; button ergonomics not manually certified |
| Locomotion/foot planting/controller | Not implemented or tested in this bounded proof |

The numerical engine test reconstructs imported linear skinning on CPU using
Godot bone poses, bind transforms and vertex weights, then compares mesh bounds
with independently evaluated Blender reimport bounds. It does not assert every
vertex is identical, nor test collisions inside Godot. Collision checks cover
actual exported geometry at 30 Hz; between-frame/extreme-pose clearance is not
certified. Seven GPU captures complement those numerical checks; they are not
headless screenshots or evidence of a complete walk.

## Problems found and resolved

- Default export starts at 1/30 second: explicitly slide the action to zero.
- Blender reference import must be set to 30 fps *before* loading the GLB;
  changing fps afterward gives incorrect reference timing.
- Default Godot import settings produced up to 6.36 mm bounds discrepancy.
  Disable animation optimisation, mesh compression and automatic LODs for this
  fidelity proof. The final settings pass the 0.1 mm comparison. These are proof
  settings, not a permanent prohibition on measured production optimisation.
- UV/material seams split vertex indices in glTF. Collision adjacency must use
  geometric corners to avoid counting shared seams as self-intersections.
- Initial thin-cloth shadow acne was addressed through the review light's shadow
  bias. The source cloth geometry was not inflated to hide a rendering issue.

## Remaining limitations

Exporter warnings are recorded, not hidden: more than eight weights on some
vertices are reduced; multiple image-node sampler warning on source materials.
The resulting eight-weight GLB passes the recorded tests. Texture appearance
is visually usable in Godot, but exact Blender shader equivalence and final
artistic skin/eye quality are not claimed. Cloth's post-armature Smooth modifier
is baked at rest for export; this test covers the resulting skinning, not dynamic
Blender smoothing equivalence. More demanding walk poses must be tested anew.

No rig replacement, retargeting, walk cycle, animation controls framework, combat,
new branches or merges. Human artistic approval and the full first milestone
remain separate from this technical handoff.

## Reproduce

Verified executables: Blender 5.2.3 LTS `e13b728c6880`; Godot 4.5.2 stable
`6ce3de25a`. Godot was extracted from the user's existing
`Godot_v4.5.2-stable_win64.exe.zip` into a temporary folder; no system installation
or engine-version change. MPFB does not need to run; building uses saved rig data
and the original installed MPFB images. The animated derivative and exported GLB
have the used textures embedded for independent viewing.

From the repository root in PowerShell:

```powershell
$blenderExe = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$godotExe = "$env:TEMP\gauntlands-godot-4.5.2\Godot_v4.5.2-stable_win64_console.exe"
& $blenderExe --background --factory-startup 'assets/Blender Models/Human-Male-180cm.blend' --python-exit-code 1 --python tools/blender/build_animation_proof.py
& $blenderExe --background --factory-startup --python-exit-code 1 --python tools/blender/test_animation_export.py
& $godotExe --headless --editor --path prototype --quit
& $godotExe --headless --path prototype --script res://tests/test_import.gd
& $godotExe --path prototype -- --capture
```

All five operations were run successfully. GPU capture was launched as a hidden
background process with output/error logs; the image files are actual viewport
captures. Rebuild overwrites the generated Animation-Proof .blend and GLB;
preserve any manual edits to those derivatives before running it. It never saves
over the accepted 180cm source. Run Blender validation before Godot comparison:
the latter rejects a reference generated from a different GLB hash.

## Asset provenance

Existing MPFB human and rig are inherited from the accepted model; no external
animation was downloaded. Diagnostic keyframes and fitted briefs are project
work. Packed textures: `young_lightskinned_male_diffuse.png` and `brown_eye.png`.
Installed MPFB `skins/young_caucasian_male/*.mhmat`, `eyes/materials/brown.mhmat`
and `eyes/high-poly/high-poly.mhclo` explicitly declare CC0 release in September
2020 and name Data Collection AB, Joel Palmius and Jonas Hauquier. These were
inspected locally; no unrelated MPFB textures are packed into the new derivative.
[CC0 terms](https://creativecommons.org/publicdomain/zero/1.0/).

## Handoff and next step

R3 -> R2/R5/R6: artifacts and timing/axis/scale contracts above. Technical export
proof accepted on recorded evidence; user visual review remains available in the
viewer. Next bounded production task is a restrained idle and one in-place walk,
with tested foot contact and clothing clearance, using this same validated export
path. Then add gamepad locomotion/turning and idle-to-walk blending on the plane.

[Neutral](../tools/blender/animation_previews/godot_neutral.png) ·
[Left leg](../tools/blender/animation_previews/godot_left_leg.png) ·
[Right leg](../tools/blender/animation_previews/godot_right_leg.png) ·
[Arms](../tools/blender/animation_previews/godot_arms.png) ·
[Head](../tools/blender/animation_previews/godot_head.png) ·
[Side](../tools/blender/animation_previews/godot_side.png) ·
[Back](../tools/blender/animation_previews/godot_back.png).

Technical references: [Godot 4.5 glTF API](https://docs.godotengine.org/en/4.5/classes/class_gltfdocument.html),
[Godot import optimisation defaults](https://github.com/godotengine/godot/blob/4.5/editor/import/3d/resource_importer_scene.cpp),
[Blender glTF export options](https://docs.blender.org/api/current/bpy.ops.export_scene.html).
