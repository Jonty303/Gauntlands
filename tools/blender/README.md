# Gauntlands — Prototype 01: fitted boxer briefs

**Status:** Experimental first-pass generator, **not yet executed or visually approved**.  
**Branch:** `human-prototype-01` only.  
**Intended host:** Blender 5.2.3 LTS, with the user’s MPFB 2.0.18 male human and rig. The exact combination is not yet independently tested.

## Design brief

Create plain charcoal-grey, close-fitting **boxer briefs** for the existing underwear-only male character. This is a modesty and deformation-test garment, not a general inventory/equipment system.

**Constraints:**
- Preserve `assets/Blender Models/Human-Male.blend` unchanged during initial testing.
- Make an **independent mesh** named `Gauntlands_Boxer_Briefs`; do not permanently modify the skin mesh.
- Use the body surface as the initial fit and transfer its vertex-group weights; reuse the existing Armature modifier where available.
- Flat, opaque charcoal fabric, understated dark waistband and short leg hems; no branding or unnecessary geometry.
- Do not generate a second character, armour, hairstyles, weapons or expanded gameplay.

## Try it on your Windows desktop

1. Ensure the Gauntlands checkout is on `human-prototype-01` and pull this commit safely (check `git status` first; do not discard local changes).
2. Open **Human-Male.blend** in Blender.
3. **Save As** a separate test file such as `Human-Male-Briefs-test.blend` **before** experimenting, rather than overwriting the committed original.
4. In **Object Mode**, click the main human **body mesh** in the Outliner. Do not select the armature or an eye.
5. Open Blender's **Scripting** workspace, then **Text → Open** and choose `tools/blender/generate_briefs.py` from your cloned checkout.
6. Click **Run Script** (Alt+P when the script editor has focus).
7. Return to **Layout**, enable **Material Preview**, and inspect the new object **Gauntlands_Boxer_Briefs**. The generator does not save the scene automatically.
8. Check front, back and side views plus a raised-knee / walking pose if the rig is available. If satisfactory, save the **test copy**, then commit it to the **prototype branch only** after review.

## Expected results

- One new, editable mesh with a charcoal material and darker waistband/leg edging.
- It should sit just outside the source skin surface; a Solidify modifier adds minimal thickness.
- Existing body rig deform weights are transferred to the matching cloth vertices. Where the source has an Armature modifier, the generated object references the same armature.
- The body mesh and original file are not automatically altered or saved.

## What to examine / known limitations

The first pass selects a pelvis/upper-thigh **surface patch** using height ratios and excludes likely arm/hand weights. It is deliberately simple: it does **not** yet rebuild a bespoke garment topology, bridge every crotch gap, add UVs, or prove weight deformations. It may need manual editing if the MPFB body proportions, anatomy or vertex distribution differ.

Inspect closely for:
- gaps across the crotch or exposed underlying anatomy;
- uneven waistband or leg hem (surface patch boundaries follow source polygons);
- intersections, especially when raising the leg or rotating the hip;
- whether the shorts follow the armature correctly and materials export to GLB.

If the wrong mesh is used, delete only the newly generated briefs, select the correct main body mesh and rerun. The script refuses to overwrite an existing `Gauntlands_Boxer_Briefs` object.

To change the fit, edit the constants at the top of the script: `WAIST_HEIGHT`, `LEG_HEM_HEIGHT`, `MAX_SIDE_REACH`, `MAX_FRONT_BACK_REACH` and `SURFACE_GAP`. Ratios are relative to the body's height. Rerun on a fresh test copy or remove the generated object first.

## Acceptance criteria

- [ ] Original human mesh remains unchanged.
- [ ] Separate briefs object appears with suitable, opaque coverage from all angles.
- [ ] Waist and leg openings sit acceptably without obvious clipping.
- [ ] Mesh follows the existing rig during basic hip and knee poses.
- [ ] Test .blend saves, closes and reopens.
- [ ] User approves visual quality before declaring the garment finished.

**Validation performed:** Python syntax check of the generated script outside Blender. **Not performed:** running against the committed `.blend`, MPFB evaluation, rig pose tests, GLB export, or Godot import. Keep failures and screenshots in the prototype review record.

This experimental garment is restricted to the first-human prototype; approval of this test does not authorise an equipment system or additional branches.
