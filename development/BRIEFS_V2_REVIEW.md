# Boxer-briefs v2 failure analysis and review

8 November 2026. Request: repair the rejected underwear generator on existing
`human-prototype-01`; no branches/merges, no source-human overwrite.
Primary: R3 Character & Technical Artist. R4 visual and R6 test reviews performed
sequentially by the same agent; these are not independent or human sign-offs.
The user's repair request authorises this bounded implementation.

## Inspected evidence

Both supplied screenshots were recovered from the referenced conversation and
visually inspected. They show knee/low-thigh placement, ragged edges, side
protrusions, and a central V/open area. Committed input revision:
`6d9ff72ee8820528f4f95380b82980f692170815`.

The actual `.blend` opens in installed Blender **5.2.3 LTS**, build e13b728c6880.
`bpy.data.version` is `(5, 2, 45)` (file schema, not a claim of patch 45).
Installed MPFB extension manifest says **2.0.18**. Tests run with factory startup,
so they validate the saved MPFB result rather than MPFB generation APIs.

`Human` contains 19,158 base vertices and 18,486 polygons, active MPFB shape keys,
an Armature modifier and a `Hide helpers` Mask using the `body` vertex group.
Visible evaluated skin has 13,380 vertices. Object/rig matrices are identity;
X is lateral, negative Y is forward (verified from feet), Z is up. Rig is
`Human.rig`, with MPFB pelvis, split upper-leg and spine deform bones; no pose
transforms were active. The other mesh, `Human.high-poly`, is the eyes, not skin.

## Why v1 failed

1. **Wrong geometry state.** `body.data.vertices` accesses the undeformed basis,
   not the active shape-key mix. Basis Z bounds are -0.023455 to 1.671095,
   height 1.694550. Evaluated visible skin spans approximately 0 to 2.430801.
   Thus v1's 0.585 waist fraction placed the top at Z **0.967857**, with hem at
   **0.696729**. The actual hip joints are near Z **1.368246**, and the v2 waist
   landmark is near Z **1.484238**. This is not primarily a world-vs-local
   rotation bug on this file: transforms are identity. It is a basis-vs-evaluated
   mesh and anatomy-assumption bug. Global body fractions also cannot establish
   a robust waist/crotch/hem contract across different proportions.
2. **Hidden helpers became clothing.** Re-running v1's selection on `Human`
   produced 974 candidate faces. The largest-area connected patch was 236 faces,
   with all 284 selected vertices in **HelperGeometry / helper-tights**. None
   of those vertices were selected from visible skin. The algorithm ignored the
   Mask modifier. Its largest connected component heuristic ranked a hidden
   clothing cage above the skin; connectivity and area do not identify anatomy.
3. **The helper was copied in its undeformed state.** No shape keys were copied
   or baked into the garment. Copying weights alone does not reproduce MPFB body
   shape. This explains why the garment remained small/low relative to the rig.
4. **Whole-face centre tests cannot make hems.** They include polygons straddling
   the cutoff and reject their neighbours, creating stepped boundaries. The
   largest-patch filter can discard required islands; it never sews missing
   surfaces, constructs a crotch, validates three openings or checks manifoldness.
5. **Normal offsets and Solidify cannot repair topology.** Offsetting the wrong
   cage preserves protrusions; Solidify only thickens/rims existing faces. It does
   not turn an open V into a fitted crotch. Materials cannot address any of this.
6. **Body selection was ambiguous.** Any selected mesh with >=400 faces qualified,
   including the 1,020-face eyes. In this saved scene the active eyes cause v1's
   automatic path to fail before generation. V2 identifies the MPFB skin explicitly.

## Replacement and handoff

R3 -> R4/R6: `tools/blender/generate_briefs.py`, test harness, six previews and JSON
measurements. New topology is generated from rings plus a shared crotch bridge;
no body/helper polygons are extracted. Evaluated, masked skin supplies fit and
interpolated deform weights. The rig supplies anatomical axes and landmarks.
Weight smoothing below the waistband reduces abrupt influence transitions.
A four-pass post-armature Smooth modifier prevents compressed groin faces from
folding through each other in the tested raised-leg pose. Rig weights
are normalised and the original armature is referenced by a separate object.

Interface: source units retained; measured hip separation scales ease/thickness;
64 waist vertices, 44 per leg opening; one UV map; two opaque materials; no textures;
1,280 quads / 2,560 base triangles, 5,424 after thickness. Budgets set for this task:
5,000 base and 6,000 thickened triangles. Pivot follows the anatomical frame under
the original armature. Facing sheets, sprite pivots and animation event timing are
not applicable to this Blender-only generator. No engine files changed.

Provenance: original procedural garment code; existing user-supplied MPFB human
is only sampled, not redistributed as a new committed asset. No external clothing
or textures added. This review does not certify the original human's full asset
licence chain or authorise runtime integration.

## Validation record and limits

Actual commands: Blender `--version`; background factory-startup inspection of
objects, evaluated shape keys, mask, bones and source selection; background
`--python-exit-code 1 --python tools/blender/test_briefs.py`; Python syntax
compilation; `git diff --check`. See the README for the exact reusable command and
[validation.json](../tools/blender/previews/validation.json) for measured results.

The harness checks original body data and source file SHA, repeat generation,
normalised weights, UV presence, topology, solidified skin/self intersections in
standing and two explicit hip poses, and save/reopen. R4 reviewed actual rendered
front/side/back/underneath and pose views for coverage and silhouette. R6's result
is limited to those tests, not full animation acceptance. Render shading is
Workbench studio lighting, not a production material/render approval.

Blender emitted a thumbnail-cache write error for the user's `.thumbnails` folder
under restricted execution. The separately saved `.blend` reopened successfully;
this did not prevent geometry tests or PNG rendering. No permission escalation
was used to modify that unrelated cache.

No Godot run: no Godot code, scenes, imports or runtime assets changed. Full walk,
deep squat, both-leg motion, exports, other body proportions and interactive MPFB
editing remain unverified. User character approval and any merge remain pending.
