# Prototype 02 — animation viewer (test 03)

9 November 2026. R2 lead; R3 asset and R6 validation responsibilities performed
by the same agent. Owner authorised this viewer before retiring Prototype 02.
The later instruction explicitly allows sprint **only in the selector**.
Owner accepted the preceding idle/walk/run test as excellent. On 9 November
2026 the owner accepted this resource-evaluation milestone, explicitly excepting
arrow firing. See the [checkpoint and open issue](../../development/PROTOTYPE_02_CHECKPOINT.md).

## Launch and controls

Open ../../prototype/project.godot in Godot 4.5.2 and press F5. The main scene is
[the action viewer](../../prototype/dummy_actions.tscn). Licensed local assets
must be built first on a fresh checkout.

| Control | Result |
| --- | --- |
| A / Space / Play button | Play or restart the selected clip; equip its props |
| LB / RB, [ / ], dropdown | Previous/next selection, wrapping at either end |
| B / Escape | Cancel and return to movement |
| Left stick / WASD / arrows | Approved walk/run movement; new input cancels preview |
| Shift | Keyboard run; top movement speed remains 4 m/s |
| Y / 1, 2, 3 | Isometric, raised 3/4, top-down |
| D-pad left/right, Q/E, Rotate button | Turn the review facing by 45 degrees |
| Start / P | Pause/resume |
| R | Reset position and return to locomotion |
| Playback dropdown | 0.5x, 1x, 1.5x preview speed |

Holding the stick while pressing A does not immediately cancel the action: the
input must return to neutral first. Loops continue until cancelled. Death/Fall
hold their last pose. Other clips automatically return to locomotion. Selection
stops the old preview; A plays the newly selected entry. Props are visible during
playback. Weapons are not persistent equipment outside the action viewer.

## Catalogue and scope

[Catalogue](../../prototype/action_catalogue.json): **113 entries**: 112 unique
supplied male in-place actions, plus a complete bow-shot sequence.

| Category | Entries |
| --- | ---: |
| Combat | 11 |
| Archery / equipment | 14 |
| Spellcasting | 19 |
| Alternate idles and idle transitions | 10 |
| General: jump, landing, falling, talk, turns | 7 |
| Directional movement, including five selectable sprints | 27 |
| Crafting, gathering, farming, fishing, hammering, mining | 25 |

Duplicate pack clips, duplicate root-motion variants, bind poses and standalone
masked pose layers are omitted. Female/dwarf models and paid packs are outside
this male-dummy test. No damage, targets, hitboxes, inventory, projectiles, spell
VFX or scenery interactions are implemented. Sprint is not added to the stick
speed mapping or locomotion blend. Selecting a movement clip plays it in place.

Equipment: left/right swords, greatsword, polearm, shield, bow/arrow, hammer,
pickaxe, plough and fishing pole. The native melee grip transforms are retained.
Crafting props use the supplied hand-prop sockets. Archery uses the separate
supplied bow rig, a visible deforming string and corrected forward arrow.
Sheathing uses a viewer-only hand/back transfer. The complete bow action joins
Load + 0.3 s Hold + Release (1.9333 s); the arrow hides 0.1 s after release.

## Rebuild and interfaces

[build_actions.py](build_actions.py) reads the owner's licensed downloads from
S:/OneDrive/__Github/Human. It never edits those downloads. Blender 5.2.3 LTS
was verified here. Run from the Prototype 02 checkout, using the installed
Blender and Godot executables (or their PATH equivalents):

```powershell
blender --background --factory-startup --python tools/kevin_actions/build_actions.py -- S:/OneDrive/__Github/Human
godot --headless --editor --path prototype --quit
godot --headless --path prototype --script res://tests/test_dummy_actions.gd
godot --headless --path prototype --script res://tests/test_dummy_locomotion.gd
godot --path prototype --script res://tests/capture_dummy_actions.gd --fixed-fps 60
python tools/kevin_actions/package_previews.py
```

Optional last builder argument: basic, melee, archer, magic or crafting. All five
must exist before a partial rebuild can produce the complete catalogue. Pillow
is required only for packaging contact sheets. This session used its previously
installed temporary library through PYTHONPATH, not a new project dependency.

Native sources: Basic 2.4, Melee 2.0.2, Archer 2.0, Spellcasting 2.0, Crafting
2.2.1. Each build_*.json records archive hashes, export hash, bytes, bone count
and source-to-bake checks. Archive extraction is local to .local/kevin.
Generated GLBs/imports/pack metadata stay in the gitignored
prototype/assets/kevin_local/actions directory. No licensed standalone assets
are added to Git. Publisher and licence references are in the
[original trial record](../kevin_walk/README.md).

Interface: metres, Blender -Y / Godot +Z forward; frame 1 source origin at 30 fps,
baked at 60 Hz and slid to time zero. FBX Take/LocalTime metadata provides the
intended clip duration; padded native action ranges are not used. A plain
56-bone B-prefixed skeleton replaces the control rig. Archer adds six bow bones
and two sword-transfer bones (64 total). Body mesh and rest rig stay native to
each pack; this is not retargeting. The preview swaps pack actors at one world
position and blends local bone poses for 0.16 s entry / 0.18 s return.

Imports preserve names (Godot suffix processing disabled), use 60 fps, eight
skin influences, disabled animation optimisation, disabled mesh compression and
no generated LODs. Each native action is primed at its end and start before
sampling; quaternion hemispheres are kept continuous. Source control dependency
cycle warnings remain in Blender, while exported rigs have none of those constraints.

Source skin minima sampled at 60 Hz supply a root-only clearance curve. The
viewer adds 4 mm because the imported/interpolated skin showed up to 3.8 mm
additional downward deviation. This is a measured preview allowance, not a
universal character rule. Positive authored jump/flight height is preserved.

## Validation actually performed

- Godot 4.5.2 headless editor import: pass after the fixes below.
- Every one of 113 entries: duration, expected visible props, finite bone poses,
  body bounds and nine sampled floor positions, pause, loop/hold/one-shot
  behaviour and return to movement: pass. [Report](validation.json).
- Tightened final sampled floor gate: above -1 mm; actual minimum
  **0.711 mm**. Source-to-bake surface gate: under 3 mm at start/mid/end;
  actual maximum **0.796 mm**. These are sampled checks, not a continuous
  collision proof.
- Synthetic A/B/LB/RB/Y/Start mappings, actual Godot A/B/RB event dispatch and
  dropdown selection: pass. Physical controller was detected as XInput but was
  **not physically operated** by the agent.
- Approved locomotion regression: pass; Walk bone difference 0; 30/60/120 Hz
  across all three views and eight run-to-walk-to-idle phases remain valid.
  Joystick still reaches 4 m/s Run, and has no Sprint animation.
- Rendered 675 frames: 113 poses x 3 views, 11 action sequences x 8 frames x 3
  views, and sword/bow/spell poses x 8 facings x 3 views. All 15 catalogue sheets,
  11 sequence sheets and 3 facing sheets were visually inspected. Captures used
  Godot's compatibility renderer on the RTX 2070. Sampled visual review passed
  for this viewer. Later owner review accepted resource sufficiency but rejected
  arrow firing; the recorded automated passes do not cover that visual defect.
- Approved original dummy Walk/Idle/Run exports and source scene scripts are
  preserved; original locomotion scene remains runnable with F6.

The current build was executed for all five packs, followed by the corrected
archer-only rebuild. A second complete byte-for-byte rebuild and a formal
runtime performance budget were not performed for this catalogue.

## Failed attempts and confirmed fixes

1. Godot stripped the _Loop suffix from five crafting clips, so their catalogue
   IDs failed. Disabling nodes/use_name_suffixes preserves exact clip IDs.
2. Three-point floor offsets missed jump penetration. Per-frame source minima
   fixed this; a measured 4 mm import allowance then resolved the small remaining
   melee skin/interpolation differences. No gait joint rotations were changed.
3. First arrow attachment pointed backwards. Its local +Z shaft needs a -90
   degree X rotation into the right hand-prop socket. Final views show forward
   arrows and the added string; release restores the string and hides the arrow.
4. A sword parented only to the hand followed it back out of the sheathing pose.
   Dedicated preview prop bones now transfer between hand and back.
5. Source mesh validation removes the invalid-mesh exporter warning. Source
   control-rig dependency-cycle warnings are documented, not claimed fixed.
6. An early capture stopped on the known missing loop clips. The final capture
   run completed all 675 frames without script errors.

## Handoff and remaining review

R3 -> R2/R6: local pack GLBs + catalogue + five build reports, for this animation
viewer only. Units, bone names, clip timings, props and import settings are above.
R2/R6 checked their interfaces in the actual engine and reviewed the rendered
output. Same-agent technical handoff accepted. Owner accepted resource sufficiency,
with P02-ARCHERY-01 (arrow firing) explicitly open. Agent-operated physical
controller testing remains not performed. Skin/clothing variants, persistent loadouts, gameplay blending and real
combat integration belong to a separately authorised next prototype.

The [owner recording review](owner_arrow_review.jpg) and [metadata](owner_arrow_report.json)
are evidence for the open firing issue, not a completed fix.
